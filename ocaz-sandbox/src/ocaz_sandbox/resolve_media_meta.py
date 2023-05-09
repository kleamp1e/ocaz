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

from .db import get_database

COLLECTION_URL = "url"
COLLECTION_OBJECT = "object"


def resolve_media_meta() -> None:
    pass


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
@click.option("--max-records", type=int, default=None, show_default=True)
@click.option("--max-workers", type=int, required=True, default=4, show_default=True)
def main(log_level: str, mongodb_url: str, max_records: int, max_workers: int) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s pid:%(process)d %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")
    logging.debug(f"mongodb_url = {json.dumps(mongodb_url)}")
    logging.debug(f"max_records = {json.dumps(max_records)}")
    logging.debug(f"max_workers = {json.dumps(max_workers)}")

    resolve_media_meta()

    logging.info("done")


if __name__ == "__main__":
    main()
