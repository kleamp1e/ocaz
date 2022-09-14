#!/usr/bin/env python3

import logging
import os
import sys

import click


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))
from ocaz.object_util import get_object_info


@click.command()
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(["info", "debug"]),
    default="info",
    help="log level",
)
@click.option(
    "-d",
    "--data-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="data directory path",
)
@click.argument("url")
def main(
    log_level: str,
    data_dir: str,
    url: str,
) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    logging.info("log_level = %s", log_level)
    logging.debug("url = %s", url)
    logging.debug("data_dir = %s", data_dir)

    object_info = get_object_info(url)
    object_id = object_info["object_id"]
    logging.debug("object_info = %s", object_info)
    logging.info("object_id = %s", object_id)

    logging.info("done")


if __name__ == "__main__":
    main()
