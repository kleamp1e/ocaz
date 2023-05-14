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


def get_url_from_url_sha1(mongodb: pymongo.database.Database, url_sha1: str) -> Optional[str]:
    if record := mongodb[COLLECTION_URL].find_one({"_id": url_sha1}, {"url": True}):
        return record["url"]
    else:
        return None


def get_url_from_head_10mb_sha1(mongodb: pymongo.database.Database, head_10mb_sha1: str) -> Optional[str]:
    if record := mongodb[COLLECTION_URL].find_one({"head10mbSha1": head_10mb_sha1, "available": True}, {"url": True}):
        return record["url"]
    else:
        return None


def get_head_10mb_sha1_from_sha1(mongodb: pymongo.database.Database, object_id: str) -> Optional[str]:
    if record := mongodb[COLLECTION_OBJECT].find_one({"sha1": object_id}, {"_id": True}):
        return record["_id"]
    else:
        return None


OCAZ_MONGODB_URL = os.environ.get("OCAZ_MONGODB_URL", None)

mongodb = get_database(OCAZ_MONGODB_URL)

app = fastapi.FastAPI()


@app.get("/")
def get_root() -> Any:
    return {}


@app.get("/url/sha1/{url_sha1}")
def get_url_sha1(url_sha1: str) -> Any:
    if is_sha1(url_sha1) and (url := get_url_from_url_sha1(mongodb, url_sha1)):
        return RedirectResponse(url)
    else:
        raise not_found()


@app.get("/object/head10mbSha1/{head_10mb_sha1}")
def get_object_head_10mb_sha1(head_10mb_sha1: str) -> Any:
    if is_sha1(head_10mb_sha1) and (url := get_url_from_head_10mb_sha1(mongodb, head_10mb_sha1)):
        return RedirectResponse(url)
    else:
        raise not_found()


@app.get("/object/sha1/{object_sha1}")
def get_object_sha1(object_sha1: str) -> Any:
    if (
        is_sha1(object_sha1)
        and (head_10mb_sha1 := get_head_10mb_sha1_from_sha1(mongodb, object_sha1))
        and (url := get_url_from_head_10mb_sha1(mongodb, head_10mb_sha1))
    ):
        return RedirectResponse(url)
    else:
        raise not_found()
