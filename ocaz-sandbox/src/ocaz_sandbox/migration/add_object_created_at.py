import json
import logging
from datetime import datetime

import click

from ..command import option_log_level, option_mongodb_url
from ..db import get_database


def add_object_created_at(
    mongodb_url: str,
) -> None:
    mongodb = get_database(mongodb_url)

    for record in mongodb["object"].find({"createdAt": {"$exists": False}}).sort([("_id", 1)]):
        logging.info(f"record = {record}")
        if "updatedAt" in record:
            new_record = {"createdAt": record["updatedAt"]}
        else:
            new_record = {
                "createdAt": datetime.now().timestamp(),
            }

        logging.info(f"new_record = {new_record}")
        mongodb["object"].update_one(
            {"_id": record["_id"]},
            {
                "$set": new_record,
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

    add_object_created_at(mongodb_url=mongodb_url)

    logging.info("done")


if __name__ == "__main__":
    main()
