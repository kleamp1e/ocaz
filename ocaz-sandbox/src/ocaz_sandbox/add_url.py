import hashlib
import json
import logging
import sys
from typing import List
from urllib.parse import urlparse

import click
import more_itertools
import pymongo

from .command import option_log_level, option_mongodb_url
from .db import get_database

COLLECTION_URL = "url"


def read_urls_from_stdin() -> List[str]:
    urls = []
    while url := sys.stdin.readline():
        urls.append(url.strip())
    return urls


def make_url_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def bulk_upsert_urls(mongodb: pymongo.database.Database, urls: List[str]) -> None:
    logging.info(f"urls.length = {len(urls)}")
    operations = [
        pymongo.UpdateOne(
            {"_id": make_url_id(url)},
            {
                "$set": {
                    "url": url,
                    "host": urlparse(url).netloc,
                }
            },
            upsert=True,
        )
        for url in urls
    ]
    mongodb[COLLECTION_URL].bulk_write(operations)


def add_url(mongodb_url: str, chunk_size: int, urls: List[str]) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"chunk_size = {chunk_size}")
    logging.debug(f"urls.length = {len(urls)}")

    mongodb = get_database(mongodb_url)

    for chunked_urls in more_itertools.chunked(urls, chunk_size):
        bulk_upsert_urls(mongodb, chunked_urls)


@click.command()
@option_log_level
@option_mongodb_url
@click.option("--stdin/--no-stdin", type=bool, default=False)
@click.option("--chunk-size", type=int, default=1000, show_default=True, required=True)
@click.argument("urls", type=str, nargs=-1)
def main(log_level: str, mongodb_url: str, stdin: bool, chunk_size: int, urls: List[str]) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")
    logging.debug(f"stdin = {json.dumps(stdin)}")

    urls = list(urls)
    if stdin:
        urls.extend(read_urls_from_stdin())

    add_url(mongodb_url=mongodb_url, chunk_size=chunk_size, urls=urls)

    logging.info("done")


if __name__ == "__main__":
    main()
