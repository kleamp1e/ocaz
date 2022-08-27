#!/usr/bin/env python3

import logging

import click


@click.command()
@click.option("--log-level", help="log level", default="info")
@click.argument("url")
def main(log_level: str, url: str) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    logging.info("log_level = %s", log_level)
    logging.debug("url = %s", url)


if __name__ == "__main__":
    main()
