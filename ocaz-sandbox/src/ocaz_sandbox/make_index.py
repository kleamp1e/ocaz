import json
import logging
import os

import click
import pymongo

COLLECTION_URL = "url"


def make_index(mongodb_url: str) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")

    mongodb = pymongo.MongoClient(mongodb_url).get_database()
    mongodb[COLLECTION_URL].create_index([("url", pymongo.ASCENDING)], unique=True)
    mongodb[COLLECTION_URL].create_index([("head10mbSha1", pymongo.ASCENDING)])


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
