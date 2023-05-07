#!/usr/bin/env python3

import logging
import os
import sys
import pathlib

import click


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))
from ocaz.meta import get_meta_info, make_meta_json_path
from ocaz.util.json import save_json


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

    logging.debug("log_level = %s", log_level)
    logging.debug("data_dir = %s", data_dir)
    logging.debug("url = %s", url)

    meta_info = get_meta_info(url)
    logging.debug("meta_info = %s", meta_info)

    object_id = meta_info["objectId"]
    logging.info("object_id = %s", object_id)

    meta_json_path = make_meta_json_path(pathlib.Path(data_dir), object_id)
    save_json(path=meta_json_path, data=meta_info)
    logging.info("meta_json_path = %s", meta_json_path)

    logging.info("done")


if __name__ == "__main__":
    main()
