import hashlib
import json
import logging
import os
import re
from typing import Any, Optional

import fastapi
import pymongo
from fastapi.responses import RedirectResponse

from .db import COLLECTION_OBJECT, COLLECTION_URL, get_database


def not_found() -> fastapi.HTTPException:
    return fastapi.HTTPException(status_code=404, detail="not found")


SHA1_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def is_sha1(sha1: str) -> bool:
    return SHA1_PATTERN.match(sha1) is not None


def get_url_from_head_10mb_sha1(mongodb: pymongo.database.Database, head_10mb_sha1: str) -> Optional[str]:
    if record := mongodb[COLLECTION_URL].find_one({"head10mbSha1": head_10mb_sha1, "available": True}, {"url": True}):
        return record["url"]
    else:
        return None


OCAZ_MONGODB_URL = os.environ["OCAZ_MONGODB_URL"]
CACHE_DIR = os.environ["CACHE_DIR"]
logging.debug(f"OCAZ_MONGODB_URL = {json.dumps(OCAZ_MONGODB_URL)}")
logging.debug(f"CACHE_DIR = {json.dumps(CACHE_DIR)}")

mongodb = get_database(OCAZ_MONGODB_URL)

app = fastapi.FastAPI()


@app.get("/")
def get_root() -> Any:
    return {}


@app.get("/object/head10mbSha1/{head_10mb_sha1}")
def get_object_head_10mb_sha1(head_10mb_sha1: str, number_of_blocks: int = 10, max_size: int = 300) -> Any:
    config = {
        "numberOfBlocks": number_of_blocks,
        "maxSize": max_size,
    }
    config_json = json.dumps(config, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    print(config_json)
    config_key = hashlib.sha1(config_json.encode("utf-8")).hexdigest()
    print(config_key)

    if is_sha1(head_10mb_sha1) and (url := get_url_from_head_10mb_sha1(mongodb, head_10mb_sha1)):
        return RedirectResponse(url)
    else:
        raise not_found()
