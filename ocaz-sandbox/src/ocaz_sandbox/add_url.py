#!/usr/bin/env python3

import hashlib
import json
import logging
import os
import sys

import click
import more_itertools
import pymongo

COLLECTION_URL = "url"


def make_url_id(url):
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def read_urls_from_stdin():
    urls = []
    while url := sys.stdin.readline():
        urls.append(url.strip())
    return urls


def add_urls_into_mongodb(mongo_db, urls):
    logging.info(f"urls.length = {len(urls)}")
    operations = [
        pymongo.UpdateOne(
            {"_id": make_url_id(url)},
            {
                "$set": {
                    "url": url,
                }
            },
            upsert=True,
        )
        for url in urls
    ]
    mongo_db[COLLECTION_URL].bulk_write(operations)


@click.command()
@click.option(
    "--mongodb-url",
    type=str,
    required=True,
    default=os.environ.get("OCAZ_MONGODB_URL", None),
)
@click.option("--stdin/--no-stdin", type=bool, default=False)
@click.argument("urls", type=str, nargs=-1)
def main(mongodb_url, stdin, urls):
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")

    target_urls = []
    target_urls.extend(list(urls))
    if stdin:
        target_urls.extend(read_urls_from_stdin())

    logging.info(f"target_urls.length = {len(target_urls)}")

    mongo_db = pymongo.MongoClient(mongodb_url).get_database()
    mongo_db[COLLECTION_URL].create_index([("url", pymongo.ASCENDING)], unique=True)
    mongo_db[COLLECTION_URL].create_index([("head10mbSha1", pymongo.ASCENDING)])

    for urls in more_itertools.chunked(target_urls, 1000):
        add_urls_into_mongodb(mongo_db, urls)

    logging.info("done")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
    )
    main()
