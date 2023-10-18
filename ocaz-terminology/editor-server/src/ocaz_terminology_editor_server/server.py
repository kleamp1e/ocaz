import json
import os
import pathlib
import random
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel


def make_random_id():
    return f"{random.randint(0, 2**31 - 1):08x}"


def load_all_term_records(term_dir: pathlib.Path) -> List[Dict]:
    records = []
    for json_path in sorted(term_dir.glob("*.json")):
        with json_path.open("r") as f:
            for line in f.readlines():
                record = json.loads(line)
                records.append(record)
    return records


class AddTerm(BaseModel):
    id: Optional[str]
    parent_id: Optional[str]
    representative_ja: str
    representative_en: Optional[str]


DATA_DIR = pathlib.Path(os.environ["DATA_DIR"])
TERM_DIR = DATA_DIR / "term"

app = FastAPI()


@app.get("/terms")
def get_terms():
    records = load_all_term_records(TERM_DIR)
    table = {}
    for record in records:
        if record["id"] in table:
            # TODO: マージする
            assert False
        else:
            table[record["id"]] = record
    return {"terms": sorted(list(table.values()), key=lambda r: r["id"])}


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

    json_path = TERM_DIR / f"{str(now)}.json"
    print(json_path)

    with json_path.open("w") as f:
        json.dump(record, f, sort_keys=True, ensure_ascii=False)

    return record
