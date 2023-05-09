import concurrent.futures
import hashlib
import json
import logging
import os
import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import click
import magic
import more_itertools
import pymongo
import requests

from .command import option_log_level, option_mongodb_url
from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"
HEAD_BLOCK_SIZE = 10 * 1000 * 1000


def find_unresolved_urls(mongodb: pymongo.database.Database, max_records: Optional[int] = None) -> Any:
    records = (
        mongodb[COLLECTION_URL]
        .find({"head10mbSha1": {"$exists": False}}, {"_id": True, "url": True})
        .sort("_id", pymongo.ASCENDING)
    )
    if max_records:
        records = records.limit(max_records)
    return records


def get_range(url: str, start_byte: int, end_byte: int) -> Any:
    return requests.get(url, headers={"Range": f"bytes={start_byte}-{end_byte}"})


def parse_content_range(content_range: str) -> Optional[Dict]:
    if content_range and (match := re.match(r"^bytes\s+(\d+)-(\d+)/(\d+)$", content_range)):
        return dict(zip(["start_byte", "end_byte", "total_size"], map(int, match.groups())))
    else:
        return None


def parse_response_headers(headers: Any) -> Dict:
    return {
        "content_length": int(headers.get("Content-Length")),
        "content_range": parse_content_range(headers.get("Content-Range")),
        "content_type": headers.get("Content-Type"),
    }


def calc_sha1(bin: bytes) -> str:
    return hashlib.sha1(bin).hexdigest()


def guess_mime_type(bin: bytes) -> str:
    return magic.from_buffer(bin, mime=True)


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


def upsert_url(mongodb: pymongo.database.Database, id: str, record: Dict) -> None:
    upsert(mongodb, COLLECTION_URL, id, record)


def resolve(mongodb_url: str, url_records: List[Dict]) -> None:
    logging.info(f"url_records.length = {len(url_records)}")

    mongodb = get_database(mongodb_url)

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
            upsert_object(mongodb, id=head_10mb_sha1, record=new_object_record)

        logging.info(f"new_url_record = {json.dumps(new_url_record)}")
        upsert_url(mongodb, id=url_record["_id"], record=new_url_record)


def resolve_object_meta(mongodb_url: str, max_records: Optional[int], max_workers: int, chunk_size: int = 100) -> None:
    mongodb = get_database(mongodb_url)

    url_records = list(find_unresolved_urls(mongodb, max_records))
    random.shuffle(url_records)
    logging.info(f"url_records.length = {len(url_records)}")

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = [
            executor.submit(resolve, mongodb_url, chunked_url_records)
            for chunked_url_records in more_itertools.chunked(url_records, chunk_size)
        ]
        for result in results:
            result.result()


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

    resolve_object_meta(mongodb_url=mongodb_url, max_records=max_records, max_workers=max_workers)

    logging.info("done")


if __name__ == "__main__":
    main()
