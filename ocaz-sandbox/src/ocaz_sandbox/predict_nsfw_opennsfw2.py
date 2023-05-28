import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import click
import pymongo
import requests

from .command import option_log_level, option_mongodb_url
from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"
OCAZ_CLASSIFIER_NSFW_OPENNSFW2_NAME = "ocaz-classifier-nsfw-opennsfw2"
OCAZ_CLASSIFIER_NSFW_OPENNSFW2_BASE_URL = "http://ocaz-classifier-nsfw-opennsfw2:8000"
TARGET_FIELD = f"image.predictions.{OCAZ_CLASSIFIER_NSFW_OPENNSFW2_NAME}"


def find_unpredicted_object_ids(mongodb: pymongo.database.Database, max_records: Optional[int] = None) -> List[str]:
    records = (
        mongodb[COLLECTION_OBJECT]
        .find({"image": {"$exists": True}, TARGET_FIELD: {"$exists": False}})
        .sort("_id", pymongo.ASCENDING)
    )
    if max_records:
        records = records.limit(max_records)
    return [record["_id"] for record in records]


def find_object(mongodb: pymongo.database.Database, object_id: str) -> Any:
    return mongodb[COLLECTION_OBJECT].find_one({"_id": object_id})


def find_url(mongodb: pymongo.database.Database, object_id: str) -> Optional[str]:
    if record := mongodb[COLLECTION_URL].find_one({"head10mbSha1": object_id, "available": True}, {"url": True}):
        return record["url"]
    else:
        return None


def predict(base_url: str, bin: bytes, file_name: str, mime_type: str) -> Dict:
    response = requests.post(
        base_url + "/classify",
        files={"file": (file_name, bin, mime_type)},
    )
    assert response.status_code == requests.codes.ok
    return response.json()


def predict_nsfw_opennsfw2(
    mongodb_url: str, classifier_nsfw_opennsfw2_base_url: str, max_records: Optional[int]
) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"classifier_nsfw_opennsfw2_base_url = {json.dumps(classifier_nsfw_opennsfw2_base_url)}")
    logging.debug(f"max_records = {json.dumps(max_records)}")
    # logging.debug(f"max_workers = {json.dumps(max_workers)}")
    # logging.debug(f"chunk_size = {json.dumps(chunk_size)}")

    mongodb = get_database(mongodb_url)

    object_ids = find_unpredicted_object_ids(mongodb=mongodb, max_records=max_records)
    print(object_ids)

    """
    # TODO: 推論が完了していないobjectレコードを取得する
    object_id = "000025890764a9e19bbb11cd140b4f8d1e69fe44"
    logging.info(f"object_id = {object_id}")

    object_record = find_object(mongodb, object_id)
    print(object_record)

    object_url = find_url(mongodb, object_id)
    logging.info(f"object_url = {object_url}")

    object_response = requests.get(object_url)
    print(object_response)
    assert object_response.status_code == requests.codes.ok
    print()

    prediction_result = predict(
        base_url=classifier_nsfw_opennsfw2_base_url,
        bin=object_response.content,
        file_name=object_id,
        mime_type=object_record["mimeType"],
    )
    print(prediction_result)

    now = datetime.now()

    operations = []
    operations.append(
        pymongo.UpdateOne(
            {"_id": object_id},
            {
                "$set": {
                    TARGET_FIELD: {
                        "version": prediction_result["service"]["version"],
                        "predictedAt": now.timestamp(),
                        "labels": prediction_result["labels"],
                    },
                    "updatedAt": now.timestamp(),
                },
            },
        )
    )
    print(operations)
    if len(operations) > 0:
        mongodb[COLLECTION_OBJECT].bulk_write(operations)
    """


@click.command()
@option_log_level
@option_mongodb_url
@click.option(
    "--classifier-nsfw-opennsfw2-base-url",
    type=str,
    default=os.environ.get("OCAZ_CLASSIFIER_NSFW_OPENNSFW2_BASE_URL", None),
    show_default=True,
    required=True,
)
@click.option("--max-records", type=int, default=None, show_default=True)
# @click.option("--max-workers", type=int, default=4, show_default=True, required=True)
# @click.option("--chunk-size", type=int, default=10, show_default=True, required=True)
# max_workers: int, chunk_size: int
def main(
    log_level: str,
    mongodb_url: str,
    classifier_nsfw_opennsfw2_base_url: str,
    max_records: Optional[int],
) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s pid:%(process)d %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")

    predict_nsfw_opennsfw2(
        mongodb_url=mongodb_url,
        classifier_nsfw_opennsfw2_base_url=classifier_nsfw_opennsfw2_base_url,
        max_records=max_records,
    )

    logging.info("done")


if __name__ == "__main__":
    main()
