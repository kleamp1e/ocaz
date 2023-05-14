import json
import logging
import random
from typing import Any, Dict, List, Optional

import click
import pymongo

from .command import option_log_level, option_mongodb_url
from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"


def find_unresolved_objects(mongodb: pymongo.database.Database, max_records: Optional[int] = None) -> Any:
    records = (
        mongodb[COLLECTION_OBJECT].find({"sha1": {"$exists": False}}, {"_id": True}).sort("_id", pymongo.ASCENDING)
    )
    if max_records:
        records = records.limit(max_records)
    return records


# def find_unresolved_urls(mongodb: pymongo.database.Database, max_records: Optional[int] = None) -> Any:
#     records = (
#         mongodb[COLLECTION_URL]
#         .find({"head10mbSha1": {"$exists": False}}, {"_id": True, "url": True})
#         .sort("_id", pymongo.ASCENDING)
#     )
#     if max_records:
#         records = records.limit(max_records)
#     return records


def resolve_sha1(mongodb_url: str, max_records: Optional[int], max_workers: int, chunk_size: int = 100) -> None:
    mongodb = get_database(mongodb_url)

    object_records = list(find_unresolved_objects(mongodb, max_records))
    random.shuffle(object_records)
    logging.info(f"object_records.length = {len(object_records)}")
    print(object_records)


@click.command()
@option_log_level
@option_mongodb_url
@click.option("--max-records", type=int, default=None, show_default=True)
@click.option("--max-workers", type=int, default=4, show_default=True, required=True)
def main(log_level: str, mongodb_url: str, max_records: Optional[int], max_workers: int) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s pid:%(process)d %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"max_records = {json.dumps(max_records)}")
    logging.debug(f"max_workers = {json.dumps(max_workers)}")

    resolve_sha1(mongodb_url=mongodb_url, max_records=max_records, max_workers=max_workers)

    logging.info("done")


if __name__ == "__main__":
    main()
