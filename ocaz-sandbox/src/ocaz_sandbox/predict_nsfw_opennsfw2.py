import concurrent.futures
import contextlib
import json
import logging
from typing import Any, List, Optional

import click
import cv2
import more_itertools
import numpy as np
import PIL.Image
import pymongo
import requests

from .command import option_log_level, option_mongodb_url
from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"
OCAZ_CLASSIFIER_NSFW_OPENNSFW2_BASE_URL = "http://ocaz-classifier-nsfw-opennsfw2:8000"


def find_object(mongodb: pymongo.database.Database, object_id: str) -> Any:
    return mongodb[COLLECTION_OBJECT].find_one({"_id": object_id})


def find_url(mongodb: pymongo.database.Database, object_id: str) -> Optional[str]:
    if record := mongodb[COLLECTION_URL].find_one({"head10mbSha1": object_id, "available": True}, {"url": True}):
        return record["url"]
    else:
        return None


def predict_nsfw_opennsfw2(mongodb_url: str) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    # logging.debug(f"max_records = {json.dumps(max_records)}")
    # logging.debug(f"max_workers = {json.dumps(max_workers)}")
    # logging.debug(f"chunk_size = {json.dumps(chunk_size)}")

    mongodb = get_database(mongodb_url)

    # TODO: 推論が完了していないobjectレコードを取得する
    object_id = "00002562b453e832e61233eadc2f883a22ad3853"
    logging.info(f"object_id = {object_id}")

    object_record = find_object(mongodb, object_id)
    print(object_record)

    object_url = find_url(mongodb, object_id)
    logging.info(f"object_url = {object_url}")

    object_response = requests.get(object_url)
    print(object_response)
    assert object_response.status_code == requests.codes.ok
    print()

    classifier_response = requests.post(
        OCAZ_CLASSIFIER_NSFW_OPENNSFW2_BASE_URL + "/classify",
        files={"file": (object_id, object_response.content, object_record["mimeType"])},
    )
    print(classifier_response)
    classifier_response_json = classifier_response.json()
    print(classifier_response_json)


@click.command()
@option_log_level
@option_mongodb_url
# @click.option("--max-records", type=int, default=None, show_default=True)
# @click.option("--max-workers", type=int, default=4, show_default=True, required=True)
# @click.option("--chunk-size", type=int, default=10, show_default=True, required=True)
# max_records: Optional[int], max_workers: int, chunk_size: int
def main(
    log_level: str,
    mongodb_url: str,
) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s pid:%(process)d %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")

    predict_nsfw_opennsfw2(mongodb_url=mongodb_url)

    logging.info("done")


if __name__ == "__main__":
    main()
