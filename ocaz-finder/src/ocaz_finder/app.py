import json
import os
from typing import Any, Optional

import fastapi
import pymongo


def get_database(mongodb_url: str) -> pymongo.database.Database:
    return pymongo.MongoClient(mongodb_url).get_database()


mongodb = get_database(os.environ["OCAZ_MONGODB_URL"])
app = fastapi.FastAPI()


@app.get("/")
def get_root() -> Any:
    return {}


@app.get("/query")
def get_query() -> Any:
    return {
        "queries": [
            {"name": "image", "object": {"condition": {"mimeType": {"$in": ["image/jpeg", "image/png", "image/gif"]}}}}
        ]
    }


@app.get("/find")
def get_find(
    condition: str,
    projection: Optional[str] = None,
    sort: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
) -> Any:
    condition = json.loads(condition)
    projection = json.loads(projection) if projection is not None else None

    records = mongodb["object"].find(condition, projection)

    if sort is not None:
        records = records.sort(json.loads(sort))
    if limit is not None:
        records = records.limit(limit)
    if skip is not None:
        records = records.skip(skip)

    return {
        "condition": condition,
        "projection": projection,
        "sort": sort,
        "limit": limit,
        "skip": skip,
        "result": list(records),
    }
