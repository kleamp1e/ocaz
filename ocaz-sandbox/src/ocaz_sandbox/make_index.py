import json
import logging

import click
import pymongo

from .command import option_log_level, option_mongodb_url
from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"


def make_index(mongodb_url: str) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")

    mongodb = get_database(mongodb_url)
    mongodb[COLLECTION_URL].create_index([("url", pymongo.ASCENDING)], unique=True)
    mongodb[COLLECTION_URL].create_index([("head10mbSha1", pymongo.ASCENDING)])
    mongodb[COLLECTION_OBJECT].create_index([("size", pymongo.ASCENDING)])
    mongodb[COLLECTION_OBJECT].create_index([("mimeType", pymongo.ASCENDING)])
    mongodb[COLLECTION_OBJECT].create_index([("sha1", pymongo.ASCENDING)])
    mongodb[COLLECTION_OBJECT].create_index([("perseptualHash", pymongo.ASCENDING)])


@click.command()
@option_log_level
@option_mongodb_url
def main(log_level: str, mongodb_url: str) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")

    make_index(mongodb_url=mongodb_url)

    logging.info("done")


if __name__ == "__main__":
    main()
