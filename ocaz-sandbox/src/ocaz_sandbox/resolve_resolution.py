#!/usr/bin/env python3

import json
import logging
import os
import random
from typing import Dict

import click
import pymongo


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

    for object_id_record in object_id_records:



    logging.info("done")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.DEBUG,
    )
    main()
