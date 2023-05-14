import concurrent.futures
import contextlib
import json
import logging
import random
from typing import Any, Dict, List, Optional

import click
import cv2
import more_itertools
import pymongo

from .command import option_log_level, option_mongodb_url
from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"

SUPPORT_MIME_TYPES = ["image/jpeg", "image/png", "image/gif", "video/mp4"]


def find_unresolved_object_ids(mongodb: pymongo.database.Database, max_records: Optional[int] = None) -> List[str]:
    records = (
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
    if max_records:
        records = records.limit(max_records)
    return [record["_id"] for record in records]


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


def is_image(mime_type: str) -> bool:
    return mime_type.startswith("image/")


def is_video(mime_type: str) -> bool:
    return mime_type.startswith("video/")


def update_object(mongodb: pymongo.database.Database, id: str, record: Dict) -> None:
    mongodb[COLLECTION_OBJECT].update_one(
        {"_id": id},
        {
            "$set": record,
        },
    )


def resolve_object(mongodb: pymongo.database.Database, object_id: str) -> None:
    logging.info(f"object_id = {object_id}")

    object_record = find_object(mongodb, object_id)
    assert object_record

    if has_media_meta(object_record):
        logging.warning("the record already has image/video meta info.")
        return

    url_record = find_url(mongodb, object_id)
    assert url_record

    url = url_record["url"]

    logging.info(f"get {url}")
    with open_video_capture(url) as video_capture:
        video_info = get_video_info(video_capture)

    logging.info(f"video_info = {json.dumps(video_info)}")

    if is_image(object_record["mimeType"]):
        del video_info["numberOfFrames"]
        del video_info["fps"]
        new_object_record = {"image": video_info}
    elif is_video(object_record["mimeType"]):
        video_info["duration"] = video_info["numberOfFrames"] / video_info["fps"]
        new_object_record = {"video": video_info}
    else:
        new_object_record = None

    logging.info(f"new_object_record = {json.dumps(new_object_record)}")
    if new_object_record:
        update_object(mongodb, object_id, new_object_record)


def resolve_objects(mongodb_url: str, object_ids: List[str]) -> None:
    logging.info(f"object_ids.length = {len(object_ids)}")

    mongodb = get_database(mongodb_url)

    for object_id in object_ids:
        resolve_object(mongodb, object_id)


def resolve_media_meta(mongodb_url: str, max_records: Optional[int], max_workers: int, chunk_size: int) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"max_records = {json.dumps(max_records)}")
    logging.debug(f"max_workers = {json.dumps(max_workers)}")
    logging.debug(f"chunk_size = {json.dumps(chunk_size)}")

    mongodb = get_database(mongodb_url)

    object_ids = find_unresolved_object_ids(mongodb, max_records)
    random.shuffle(object_ids)
    logging.info(f"object_ids.length = {len(object_ids)}")

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
@click.option("--chunk-size", type=int, default=100, show_default=True, required=True)
def main(log_level: str, mongodb_url: str, max_records: Optional[int], max_workers: int, chunk_size: int) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s pid:%(process)d %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")

    resolve_media_meta(mongodb_url=mongodb_url, max_records=max_records, max_workers=max_workers, chunk_size=chunk_size)

    logging.info("done")


if __name__ == "__main__":
    main()
