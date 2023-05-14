import concurrent.futures
import contextlib
import json
import logging
import random
from typing import Any, Dict, List, Optional

import click
import cv2
import imagehash
import more_itertools
import numpy as np
import PIL.Image
import pymongo

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


def find_url(mongodb: pymongo.database.Database, object_id: str) -> Optional[str]:
    if record := mongodb[COLLECTION_URL].find_one({"head10mbSha1": object_id, "available": True}, {"url": True}):
        return record["url"]
    else:
        return None


@contextlib.contextmanager
def open_video_capture(url: str) -> cv2.VideoCapture:
    video_capture = cv2.VideoCapture(url)
    assert video_capture.isOpened()
    try:
        yield video_capture
    finally:
        video_capture.release()


def read_frame(video_capture: cv2.VideoCapture, frame_index: int = None) -> np.ndarray:
    if frame_index:
        assert video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = video_capture.read()
    assert ret
    return frame


def cv2_image_to_pillow_image(cv_image: np.ndarray) -> PIL.Image:
    return PIL.Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))


def calc_phash_from_url(url: str) -> str:
    with open_video_capture(url) as video_capture:
        image = read_frame(video_capture)
        image = cv2_image_to_pillow_image(image)
        return str(imagehash.phash(image))


def resolve_objects(mongodb_url: str, object_ids: List[str]) -> None:
    logging.info(f"object_ids.length = {len(object_ids)}")

    mongodb = get_database(mongodb_url)

    operations = []
    for object_id in object_ids:
        logging.info(f"object_id = {object_id}")

        url = find_url(mongodb, object_id)
        logging.info(f"get {url}")

        phash = calc_phash_from_url(url)
        logging.info(f"phash = {phash}")

        operations.append(
            pymongo.UpdateOne(
                {"_id": object_id},
                {
                    "$set": {"perseptualHash": phash},
                },
            )
        )

    if len(operations) > 0:
        mongodb[COLLECTION_OBJECT].bulk_write(operations)


def resolve_phash(mongodb_url: str, max_records: Optional[int], max_workers: int, chunk_size: int) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"max_records = {json.dumps(max_records)}")
    logging.debug(f"max_workers = {json.dumps(max_workers)}")
    logging.debug(f"chunk_size = {json.dumps(chunk_size)}")

    mongodb = get_database(mongodb_url)

    object_ids = list(find_phash_unresolved_object_ids(mongodb, max_records))
    # random.shuffle(object_ids)
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
