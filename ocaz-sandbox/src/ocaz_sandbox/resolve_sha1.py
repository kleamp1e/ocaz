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


def find_sha1_unresolved_object_ids(mongodb: pymongo.database.Database, max_records: Optional[int] = None) -> Any:
    records = (
        mongodb[COLLECTION_OBJECT].find({"sha1": {"$exists": False}}, {"_id": True}).sort("_id", pymongo.ASCENDING)
    )
    if max_records:
        records = records.limit(max_records)
    return [record["_id"] for record in records]


def find_urls(mongodb: pymongo.database.Database, object_ids: List[str]) -> Any:
    records = (
        mongodb[COLLECTION_URL]
        .find({"head10mbSha1": {"$in": object_ids}}, {"_id": True, "url": True, "head10mbSha1": True})
        .sort("_id", pymongo.ASCENDING)
    )
    return records


def calc_sha1_from_url(url: str, chunk_size: int = 1000 * 1000) -> str:
    response = requests.get(url, stream=True)
    assert response.status_code == requests.codes.ok
    sha1_hash = hashlib.sha1()
    for chunk in response.iter_content(chunk_size=chunk_size):
        sha1_hash.update(chunk)
    return sha1_hash.hexdigest()


def resolve_objects(mongodb_url: str, object_ids: List[str]) -> None:
    logging.info(f"object_ids.length = {len(object_ids)}")
    print(object_ids)

    mongodb = get_database(mongodb_url)
    url_records = find_urls(mongodb, object_ids)
    url_records = list(url_records)
    print(url_records)

    operations = []
    for url_record in url_records:
        object_id = url_record["head10mbSha1"]
        logging.info(f"object_id = {object_id}")

        url = url_record["url"]
        logging.info(f"get {url}")
        sha1 = calc_sha1_from_url(url)

        new_object_record = {"sha1": sha1}
        logging.info(f"new_object_record = {json.dumps(new_object_record)}")

        operations.append(
            pymongo.UpdateOne(
                {"_id": object_id},
                {
                    "$set": new_object_record,
                },
            )
        )

    print(operations)
    mongodb[COLLECTION_OBJECT].bulk_write(operations)


def resolve_sha1(mongodb_url: str, max_records: Optional[int], max_workers: int, chunk_size: int) -> None:
    mongodb = get_database(mongodb_url)

    object_ids = list(find_sha1_unresolved_object_ids(mongodb, max_records))
    # random.shuffle(object_ids)
    logging.info(f"object_ids.length = {len(object_ids)}")
    print(object_ids)

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        try:
            results = [
                executor.submit(resolve_objects, mongodb_url, chunked_object_ids)
                for chunked_object_ids in more_itertools.chunked(object_ids, chunk_size)
            ]
            for result in results:
                result.result()
        except KeyboardInterrupt:
            executor.shutdown(wait=False)


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
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"max_records = {json.dumps(max_records)}")
    logging.debug(f"max_workers = {json.dumps(max_workers)}")
    logging.debug(f"chunk_size = {json.dumps(chunk_size)}")

    resolve_sha1(mongodb_url=mongodb_url, max_records=max_records, max_workers=max_workers, chunk_size=chunk_size)

    logging.info("done")


if __name__ == "__main__":
    main()
