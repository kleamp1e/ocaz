import json
import os
import pathlib
from typing import Any, Optional

import fastapi
import pymongo

from . import version


def get_database(mongodb_url: str) -> pymongo.database.Database:
    return pymongo.MongoClient(mongodb_url).get_database()


mongodb = get_database(os.environ["OCAZ_MONGODB_URL"])
app = fastapi.FastAPI()

SERVICE = {
    "name": "ocaz-finder",
    "version": version,
}


@app.get("/")
def get_root() -> Any:
    return {"service": SERVICE}


@app.get("/query")
def get_query() -> Any:
    query_dir = pathlib.Path(os.environ["QUERY_DIR"]).resolve()

    queries = []
    for path in sorted(query_dir.glob("**/*.json")):
        with path.open("r") as file:
            query = json.load(file)
        query["filePath"] = str(path.relative_to(query_dir))
        queries.append(query)

    return {
        "service": SERVICE,
        "queries": queries,
    }


@app.get("/find")
def get_find(
    collection: str,
    condition: str,
    projection: Optional[str] = None,
    sort: Optional[str] = None,
    limit: Optional[int] = 0,
    skip: Optional[int] = 0,
) -> Any:
    condition = json.loads(condition)
    projection = json.loads(projection) if projection is not None else None
    sort = json.loads(sort) if sort is not None else None

    records = mongodb[collection].find(condition, projection, sort=sort, limit=limit, skip=skip)

    return {
        "service": SERVICE,
        "settings": {
            "database": mongodb.name,
        },
        "request": {
            "collection": collection,
            "condition": condition,
            "projection": projection,
            "sort": sort,
            "limit": limit,
            "skip": skip,
        },
        "records": list(records),
    }
