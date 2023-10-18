import json
import os
import pathlib
import random
from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel


def make_random_id():
    return f"{random.randint(0, 2**31 - 1):08x}"


class AddTerm(BaseModel):
    id: Optional[str]
    parent_id: Optional[str]
    representative_ja: str
    representative_en: Optional[str]


DATA_DIR = pathlib.Path(os.environ["DATA_DIR"])

app = FastAPI()


@app.get("/about")
def get_about():
    return {}


@app.post("/term/add")
def post_term_add(body: AddTerm):
    new_id = body.id if body.id is not None else make_random_id()
    now = int(datetime.now().timestamp())
    representatives = {"ja": body.representative_ja}
    if body.representative_en is not None:
        representatives["en"] = body.representative_en

    record = {
        "id": new_id,
        "parentId": body.parent_id,
        "updatedAt": now,
        "representatives": representatives,
    }

    json_path = DATA_DIR / "tag" / f"{str(now)}.json"
    print(json_path)

    with json_path.open("w") as f:
        json.dump(record, f, sort_keys=True, ensure_ascii=False)

    return record
