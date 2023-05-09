#!/usr/bin/env python3

import contextlib
import json
import logging
import os
import random
from typing import Dict

import click
import cv2
import pymongo


@contextlib.contextmanager
def open_video_capture(url: str) -> cv2.VideoCapture:
    video_capture = cv2.VideoCapture(url)
    assert video_capture.isOpened()
    try:
        yield video_capture
    finally:
        video_capture.release()


def get_video_info(video_capture: cv2.VideoCapture) -> Dict:
    return {
        "width": int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "numberOfFrames": int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        "fps": video_capture.get(cv2.CAP_PROP_FPS),
    }


@click.command()
@click.option(
    "--mongodb-url",
    type=str,
    required=True,
    default=os.environ.get("OCAZ_MONGODB_URL", None),
)
@click.option("--limit", type=int, required=True, default=1000)
def main(mongodb_url, limit):
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")

    mongo_db = pymongo.MongoClient(mongodb_url).get_database()
    mongo_col_url = mongo_db["url"]
    mongo_col_object = mongo_db["object"]

    object_id_records = mongo_col_object.find(
        {
            "image": {"$exists": False},
            "video": {"$exists": False},
        },
        {"_id": True},
    )
    object_id_records = object_id_records.limit(limit)
    object_id_records = list(object_id_records)
    random.shuffle(object_id_records)

    for object_id_record in object_id_records:
        object_id = object_id_record["_id"]
        logging.info(f"object_id = {object_id}")

        object_record = mongo_col_object.find_one(
            {"_id": object_id},
            {"_id": True, "mimeType": True, "image": True, "video": True},
        )
        if "image" in object_record or "video" in object_record:
            logging.info("the record already has image/video info.")
            continue

        url_record = mongo_col_url.find_one({"head10mbSha1": object_id, "available": True}, {"url": True})
        url = url_record["url"]

        logging.info(f"get {url}")
        with open_video_capture(url) as video_capture:
            video_info = get_video_info(video_capture)

        if object_record["mimeType"].startswith("image/"):
            del video_info["numberOfFrames"]
            del video_info["fps"]
            new_object_record = {"image": video_info}
        elif object_record["mimeType"].startswith("video/"):
            video_info["duration"] = video_info["numberOfFrames"] / video_info["fps"]
            new_object_record = {"video": video_info}

        logging.info(f"new_object_record = {json.dumps(new_object_record)}")
        mongo_col_object.update_one(
            {"_id": object_id},
            {
                "$set": new_object_record,
            },
            upsert=True,
        )

    logging.info("done")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.DEBUG,
    )
    main()
