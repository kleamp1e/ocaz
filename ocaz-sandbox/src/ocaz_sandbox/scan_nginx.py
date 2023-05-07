#!/usr/bin/env python3

import concurrent.futures
import itertools
import logging
from urllib.parse import urljoin

import click
import requests
from bs4 import BeautifulSoup


def extract_urls(url):
    logging.info(f"fetch {url}")
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return [
        urljoin(url, href)
        for a in soup.find_all("a")
        if (href := a.get("href")) != "../"
    ]


def is_dir(url):
    return url.endswith("/")


@click.command()
@click.option(
    "--max-workers",
    type=int,
    required=True,
    default=8,
)
@click.argument("origin_url")
def main(max_workers, origin_url):
    if is_dir(origin_url):
        dir_urls = [origin_url]
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        ) as executor:
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

    logging.info("done")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
    )
    main()
