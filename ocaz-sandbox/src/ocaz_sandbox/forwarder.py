import os
import re

import pymongo
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

SHA1_PATTERN = re.compile(r"^[0-9a-f]{40}$")
OCAZ_MONGODB_URL = os.environ.get("OCAZ_MONGODB_URL", None)

app = FastAPI()

mongo_db = pymongo.MongoClient(OCAZ_MONGODB_URL).get_database()
mongo_col_url = mongo_db["url"]
mongo_col_object = mongo_db["object"]


def not_found():
    return HTTPException(status_code=404, detail="not found")


def is_sha1(sha1):
    return SHA1_PATTERN.match(sha1) is not None


def url_sha1_to_url(sha1: str) -> str:
    if record := mongo_col_url.find_one({"_id": sha1}, {"url": True}):
        return record["url"]
    else:
        return None


def object_sha1_to_head_10mb_sha1(sha1: str) -> str:
    if record := mongo_col_object.find_one({"sha1": sha1}, {"_id": True}):
        return record["_id"]
    else:
        return None


def head_10mb_sha1_to_url(sha1: str) -> str:
    if record := mongo_col_url.find_one({"head10mbSha1": sha1, "available": True}, {"url": True}):
        return record["url"]
    else:
        return None


@app.get("/")
def get_root():
    return {}


@app.get("/url/sha1/{url_sha1}")
def get_url_sha1(url_sha1: str):
    if is_sha1(url_sha1) and (url := url_sha1_to_url(url_sha1)):
        return RedirectResponse(url)
    else:
        raise not_found()


@app.get("/object/head10mbSha1/{head_10mb_sha1}")
def get_object_head_10mb_sha1(head_10mb_sha1: str):
    if is_sha1(head_10mb_sha1) and (url := head_10mb_sha1_to_url(head_10mb_sha1)):
        return RedirectResponse(url)
    else:
        raise not_found()


@app.get("/object/sha1/{object_sha1}")
def get_object_sha1(object_sha1: str):
    if (
        is_sha1(object_sha1)
        and (head_10mb_sha1 := object_sha1_to_head_10mb_sha1(object_sha1))
        and (url := head_10mb_sha1_to_url(head_10mb_sha1))
    ):
        return RedirectResponse(url)
    else:
        raise not_found()
