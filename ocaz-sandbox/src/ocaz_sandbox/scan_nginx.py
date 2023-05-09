import concurrent.futures
import itertools
import json
import logging
from typing import List
from urllib.parse import urljoin

import click
import requests
from bs4 import BeautifulSoup

from .command import option_log_level


def extract_urls(url: str) -> List[str]:
    logging.info(f"get {url}")
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return [urljoin(url, href) for a in soup.find_all("a") if (href := a.get("href")) != "../"]


def is_dir(url: str) -> bool:
    return url.endswith("/")


def scan_nginx(max_workers: int, origin_url: str) -> None:
    logging.debug(f"max_workers = {json.dumps(max_workers)}")
    logging.debug(f"origin_url = {json.dumps(origin_url)}")

    if is_dir(origin_url):
        dir_urls = [origin_url]
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            while len(dir_urls) > 0:
                new_dir_urls = []
                for sub_url in itertools.chain(*executor.map(extract_urls, dir_urls)):
                    if is_dir(sub_url):
                        new_dir_urls.append(sub_url)
                    else:
                        print(sub_url)
                dir_urls = new_dir_urls
    else:
        print(origin_url)


@click.command()
@option_log_level
@click.option(
    "--max-workers",
    type=int,
    default=4,
    show_default=True,
)
@click.argument("origin_url")
def main(log_level: str, max_workers: int, origin_url: str) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    logging.debug(f"log_level = {json.dumps(log_level)}")

    scan_nginx(max_workers=max_workers, origin_url=origin_url)

    logging.info("done")


if __name__ == "__main__":
    main()
