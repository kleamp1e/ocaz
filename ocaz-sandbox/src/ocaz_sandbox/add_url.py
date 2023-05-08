import hashlib
import json
import logging
import os
import sys
from typing import List

import click
import more_itertools
import pymongo

COLLECTION_URL = "url"


def read_urls_from_stdin() -> List[str]:
    urls = []
    while url := sys.stdin.readline():
        urls.append(url.strip())
    return urls


def make_url_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def bulk_upsert_urls(mongodb: pymongo.database, urls: List[str]) -> None:
    logging.info(f"urls.length = {len(urls)}")
    operations = [
        pymongo.UpdateOne(
            {"_id": make_url_id(url)},
            {
                "$set": {
                    "url": url,
                }
            },
            upsert=True,
        )
        for url in urls
    ]
    mongodb[COLLECTION_URL].bulk_write(operations)


def add_url(mongodb_url: str, stdin: bool, urls: List[str]) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"stdin = {json.dumps(stdin)}")
    logging.debug(f"urls.length = {len(urls)}")

    target_urls = []
    target_urls.extend(list(urls))
    if stdin:
        target_urls.extend(read_urls_from_stdin())
    logging.info(f"target_urls.length = {len(target_urls)}")

    mongodb = pymongo.MongoClient(mongodb_url).get_database()

    for urls in more_itertools.chunked(target_urls, 1000):
        bulk_upsert_urls(mongodb, urls)


@click.command()
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(["info", "debug"]),
    default="info",
    show_default=True,
    help="log level",
)
@click.option(
    "--mongodb-url",
    type=str,
    required=True,
    default=os.environ.get("OCAZ_MONGODB_URL", None),
    show_default=True,
)
@click.option("--stdin/--no-stdin", type=bool, default=False)
@click.argument("urls", type=str, nargs=-1)
def main(log_level: str, mongodb_url: str, stdin: bool, urls: List[str]) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")
    add_url(mongodb_url=mongodb_url, stdin=stdin, urls=urls)
    logging.info("done")


if __name__ == "__main__":
    main()
