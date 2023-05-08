#!/usr/bin/env python3

import hashlib
import json
import logging
import os
import random
import re
from datetime import datetime

import click
import magic
import pymongo
import requests

HEAD_BLOCK_SIZE = 10 * 1000 * 1000


def get_range(url, start_byte, end_byte):
    return requests.get(url, headers={"Range": f"bytes={start_byte}-{end_byte}"})


def calc_sha1(bin):
    return hashlib.sha1(bin).hexdigest()


def guess_mime_type(bin):
    return magic.from_buffer(bin, mime=True)


def parse_content_range(content_range):
    if content_range and (match := re.match(r"^bytes\s+(\d+)-(\d+)/(\d+)$", content_range)):
        return dict(zip(["start_byte", "end_byte", "total_size"], map(int, match.groups())))
    else:
        return None


def parse_response_headers(headers):
    return {
        "content_length": int(headers.get("Content-Length")),
        "content_range": parse_content_range(headers.get("Content-Range")),
        "content_type": headers.get("Content-Type"),
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
    mongo_col_object.create_index([("size", pymongo.ASCENDING)])
    mongo_col_object.create_index([("mimeType", pymongo.ASCENDING)])

    url_records = mongo_col_url.find({"head10mbSha1": {"$exists": False}})
    url_records = url_records.limit(limit)
    url_records = list(url_records)
    random.shuffle(url_records)

    for url_record in url_records:
        url = url_record["url"]

        logging.info(f"get {url}")
        response = get_range(url, start_byte=0, end_byte=HEAD_BLOCK_SIZE - 1)
        assert response.status_code in [requests.codes.partial, requests.codes.ok]
        response_headers = parse_response_headers(response.headers)
        assert response_headers["content_length"] <= HEAD_BLOCK_SIZE

        head_10mb_sha1 = calc_sha1(response.content)
        new_url_record = {
            "head10mbSha1": head_10mb_sha1,
            "accessedAt": datetime.now().timestamp(),
        }

        if response_headers["content_length"] == 0:
            new_url_record.update({"available": False, "error": {"detail": "content length is zero"}})
            new_object_record = None
        else:
            total_size = response_headers["content_range"]["total_size"]
            assert response.status_code == requests.codes.partial
            assert response_headers["content_range"]["start_byte"] == 0
            assert response_headers["content_range"]["end_byte"] <= response_headers["content_length"] - 1
            assert total_size > 0

            mime_type = guess_mime_type(response.content)
            if mime_type != response_headers["content_type"]:
                logging.warning(f"MIME type is not matched. {mime_type} != {response_headers['content_type']}")
            if not mime_type in ["image/jpeg", "image/png", "image/gif", "video/mp4"]:
                logging.warning(f"{mime_type} is unknown MIME type.")

            new_url_record.update({"available": True, "error": None})
            new_object_record = {
                "size": total_size,
                "mimeType": mime_type,
            }
            if total_size <= HEAD_BLOCK_SIZE:
                new_object_record.update({"sha1": head_10mb_sha1})

        logging.info(f"new_object_record = {json.dumps(new_object_record)}")
        if new_object_record:
            mongo_col_object.update_one(
                {"_id": head_10mb_sha1},
                {
                    "$set": new_object_record,
                },
                upsert=True,
            )

        logging.info(f"new_url_record = {json.dumps(new_url_record)}")
        mongo_col_url.update_one(
            {"_id": url_record["_id"]},
            {
                "$set": new_url_record,
            },
            upsert=True,
        )

    logging.info("done")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
    )
    main()
