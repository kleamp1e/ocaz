import concurrent.futures
import hashlib
import json
import logging
import random
from typing import Any, Dict, List, Optional

import click
import more_itertools
import pymongo
import requests

from .command import option_log_level, option_mongodb_url
from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"


def find_phash_unresolved_object_ids(mongodb: pymongo.database.Database, max_records: Optional[int] = None) -> Any:
    records = (
        mongodb[COLLECTION_OBJECT]
        .find({"image": {"$exists": True}, "perseptualHash": {"$exists": False}}, {"_id": True})
        .sort("_id", pymongo.ASCENDING)
    )
    if max_records:
        records = records.limit(max_records)
    return [record["_id"] for record in records]


def resolve_phash(mongodb_url: str, max_records: Optional[int], max_workers: int, chunk_size: int) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"max_records = {json.dumps(max_records)}")
    logging.debug(f"max_workers = {json.dumps(max_workers)}")
    logging.debug(f"chunk_size = {json.dumps(chunk_size)}")

    mongodb = get_database(mongodb_url)

    object_ids = list(find_phash_unresolved_object_ids(mongodb, max_records))
    # random.shuffle(object_ids)
    logging.info(f"object_ids.length = {len(object_ids)}")
    print(object_ids)


@click.command()
@option_log_level
@option_mongodb_url
@click.option("--max-records", type=int, default=None, show_default=True)
@click.option("--max-workers", type=int, default=4, show_default=True, required=True)
@click.option("--chunk-size", type=int, default=10, show_default=True, required=True)
def main(log_level: str, mongodb_url: str, max_records: Optional[int], max_workers: int, chunk_size: int) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s pid:%(process)d %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")

    resolve_phash(mongodb_url=mongodb_url, max_records=max_records, max_workers=max_workers, chunk_size=chunk_size)

    logging.info("done")


if __name__ == "__main__":
    main()
