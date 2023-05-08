import json
import logging
import os

import click
import pymongo

COLLECTION_URL = "url"

@click.command()
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(["info", "debug"]),
    default="info",
    help="log level",
)
@click.option(
    "--mongodb-url",
    type=str,
    required=True,
    default=os.environ.get("OCAZ_MONGODB_URL", None),
)
def main(log_level: str, mongodb_url: str):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")

    mongo_db = pymongo.MongoClient(mongodb_url).get_database()
    mongo_db[COLLECTION_URL].create_index([("url", pymongo.ASCENDING)], unique=True)
    mongo_db[COLLECTION_URL].create_index([("head10mbSha1", pymongo.ASCENDING)])

    logging.info("done")


if __name__ == "__main__":
    main()
