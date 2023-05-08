import concurrent.futures
import json
import logging
import os
import random
from typing import Dict, List

import click
import more_itertools
import pymongo

from .db import get_database

COLLECTION_URL = "url"


def find_unresolved_urls(mongodb: pymongo.database.Database):
    return (
        mongodb[COLLECTION_URL]
        .find({"head10mbSha1": {"$exists": False}}, {"_id": True, "url": True})
        .sort("_id", pymongo.ASCENDING)
    )


def resolve(mongodb_url: str, url_records: List[Dict]) -> None:
    logging.info(f"url_records.length = {len(url_records)}")
    print(url_records)

    mongodb = get_database(mongodb_url)


def resolve_object_meta(mongodb_url: str, max_records: int = 1) -> None:
    mongodb = get_database(mongodb_url)

    url_records = find_unresolved_urls(mongodb)
    url_records = url_records.limit(max_records)
    url_records = list(url_records)
    random.shuffle(url_records)
    print(list(url_records))

    max_workers = 1
    chunk_size = 1
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        for chunked_url_records in more_itertools.chunked(url_records, chunk_size):
            executor.submit(resolve, mongodb_url, chunked_url_records)


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
@click.option("--limit", type=int, required=True, default=1000)
def main(log_level: str, mongodb_url: str, limit: int):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s pid:%(process)d %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"limit = {json.dumps(limit)}")

    resolve_object_meta(mongodb_url)

    logging.info("done")


if __name__ == "__main__":
    main()
