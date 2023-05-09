import concurrent.futures
import contextlib
import json
import logging
import os
from typing import Any, Dict, List, Optional

import click
import cv2
import more_itertools
import pymongo

from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"

SUPPORT_MIME_TYPES = ["image/jpeg", "image/png", "image/gif", "video/mp4"]


def find_unresolved_object_ids(mongodb: pymongo.database.Database) -> List[str]:
    objects = (
        mongodb[COLLECTION_OBJECT]
        .find(
            {
                "mimeType": {"$in": SUPPORT_MIME_TYPES},
                "image": {"$exists": False},
                "video": {"$exists": False},
            },
            {"_id": True},
        )
        .sort("_id", pymongo.ASCENDING)
    )
    limit = 1
    if limit:
        objects = objects.limit(limit)
    return [object["_id"] for object in objects]


def find_object(mongodb: pymongo.database.Database, object_id: str) -> Optional[Any]:
    return mongodb[COLLECTION_OBJECT].find_one(
        {"_id": object_id},
        {"_id": True, "mimeType": True, "image": True, "video": True},
    )


def has_media_meta(object: Dict[str, Any]) -> bool:
    return "image" in object or "video" in object


def find_url(mongodb: pymongo.database.Database, object_id: str) -> Optional[Any]:
    return mongodb[COLLECTION_URL].find_one({"head10mbSha1": object_id, "available": True}, {"url": True})


@contextlib.contextmanager
def open_video_capture(url: str) -> cv2.VideoCapture:
    video_capture = cv2.VideoCapture(url)
    assert video_capture.isOpened()
    try:
        yield video_capture
    finally:
        video_capture.release()


def get_video_info(video_capture: cv2.VideoCapture) -> Dict[str, Any]:
    return {
        "width": int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "numberOfFrames": int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        "fps": video_capture.get(cv2.CAP_PROP_FPS),
    }


def upsert(mongodb: pymongo.database.Database, collection: str, id: str, record: Dict) -> None:
    mongodb[collection].update_one(
        {"_id": id},
        {
            "$set": record,
        },
        upsert=True,
    )


def upsert_object(mongodb: pymongo.database.Database, id: str, record: Dict) -> None:
    upsert(mongodb, COLLECTION_OBJECT, id, record)


def resolve(mongodb_url: str, object_ids: List[str]) -> None:
    logging.info(f"object_ids.length = {len(object_ids)}")

    mongodb = get_database(mongodb_url)

    for object_id in object_ids:
        logging.info(f"object_id = {object_id}")

        object_record = find_object(mongodb, object_id)
        print(object_record)  # DEBUG:
        if has_media_meta(object_record):
            logging.info("the record already has image/video meta info.")
            continue

        url_record = find_url(mongodb, object_id)
        url = url_record["url"]
        print(url_record)  # DEBUG:

        logging.info(f"get {url}")
        with open_video_capture(url) as video_capture:
            video_info = get_video_info(video_capture)
        logging.info(f"video_info = {json.dumps(video_info)}")

        if object_record["mimeType"].startswith("image/"):
            del video_info["numberOfFrames"]
            del video_info["fps"]
            new_object_record = {"image": video_info}
        elif object_record["mimeType"].startswith("video/"):
            video_info["duration"] = video_info["numberOfFrames"] / video_info["fps"]
            new_object_record = {"video": video_info}
        else:
            new_object_record = None

        logging.info(f"new_object_record = {json.dumps(new_object_record)}")
        if new_object_record:
            upsert_object(mongodb, object_id, new_object_record)


def resolve_media_meta(mongodb_url: str) -> None:
    mongodb = get_database(mongodb_url)

    object_ids = find_unresolved_object_ids(mongodb)
    # random.shuffle(object_ids)
    logging.info(f"object_ids.length = {len(object_ids)}")

    chunk_size = 1
    max_workers = 1
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = [
            executor.submit(resolve, mongodb_url, chunked_object_ids)
            for chunked_object_ids in more_itertools.chunked(object_ids, chunk_size)
        ]
        for result in results:
            result.result()


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
@click.option("--max-records", type=int, default=None, show_default=True)
@click.option("--max-workers", type=int, required=True, default=4, show_default=True)
def main(log_level: str, mongodb_url: str, max_records: int, max_workers: int) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s pid:%(process)d %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"max_records = {json.dumps(max_records)}")
    logging.debug(f"max_workers = {json.dumps(max_workers)}")

    resolve_media_meta(mongodb_url=mongodb_url)

    logging.info("done")


if __name__ == "__main__":
    main()
