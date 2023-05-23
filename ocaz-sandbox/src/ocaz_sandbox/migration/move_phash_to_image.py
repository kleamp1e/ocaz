import json
import logging

import click
import pymongo

from ..command import option_log_level, option_mongodb_url
from ..db import get_database

COLLECTION_OBJECT = "object"


def move_phash_to_image(
    mongodb_url: str,
) -> None:
    mongodb = get_database(mongodb_url)

    records = (
        mongodb[COLLECTION_OBJECT]
        .find({"image": {"$exists": True}, "perseptualHash": {"$exists": True}})
        .sort("_id", pymongo.ASCENDING)
        .limit(1)
    )
    records = list(records)
    for record in records:
        print(record)

        new_image = dict(record["image"])
        new_image["perseptualHash"] = record["perseptualHash"]
        print(new_image)

        mongodb[COLLECTION_OBJECT].update_one(
            {"_id": record["_id"]},
            {
                "$set": {
                    "image": new_image,
                },
            },
        )


@click.command()
@option_log_level
@option_mongodb_url
def main(log_level: str, mongodb_url: str) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s pid:%(process)d %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")

    move_phash_to_image(mongodb_url=mongodb_url)

    logging.info("done")


if __name__ == "__main__":
    main()
