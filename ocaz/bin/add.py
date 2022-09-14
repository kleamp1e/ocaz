#!/usr/bin/env python3

import logging
import os
import sys
import pathlib

import click


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))
from ocaz.object_util import get_object_info
from ocaz.path_util import make_nested_id_path
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

    object_info = get_object_info(url)
    object_id = object_info["object_id"]
    logging.debug("object_info = %s", object_info)
    logging.debug("object_id = %s", object_id)

    meta_info = {
        "url": url,
        "size": object_info["content_length"],
        "mimeType": object_info["content_type"],
        "objectId": object_id,
    }
    logging.debug("meta_info = %s", meta_info)

    meta_dir = pathlib.Path(data_dir) / "meta" / "v1"
    meta_json_path = make_nested_id_path(meta_dir, object_id, ".json")
    save_json(path=meta_json_path, data=meta_info)
    logging.info("meta_json_path = %s", meta_json_path)

    logging.info("done")


if __name__ == "__main__":
    main()
