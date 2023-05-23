import json
import logging

import click

from .command import option_log_level, option_mongodb_url
from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"


def stats(mongodb_url: str) -> None:
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")

    mongodb = get_database(mongodb_url)

    def count_url(cond):
        return mongodb[COLLECTION_URL].count_documents(cond)

    def count_object(cond):
        return mongodb[COLLECTION_OBJECT].count_documents(cond)

    logging.info(f"url = {count_url({})}")
    logging.info(f'url.available = {count_url({"available": True})}')
    logging.info(f'url.head10mbSha1 = {count_url({"head10mbSha1": {"$exists": True}})}')
    logging.info(f"object = {count_object({})}")
    logging.info(f'object.sha1 = {count_object({"sha1": {"$exists": True}})}')
    logging.info(f'object.image = {count_object({"image": {"$exists": True}})}')
    logging.info(f'object.image.perseptualHash = {count_object({"image.perseptualHash": {"$exists": True}})}')
    logging.info(f'object.video = {count_object({"video": {"$exists": True}})}')


@click.command()
@option_log_level
@option_mongodb_url
def main(log_level: str, mongodb_url: str) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")

    stats(mongodb_url=mongodb_url)

    logging.info("done")


if __name__ == "__main__":
    main()
