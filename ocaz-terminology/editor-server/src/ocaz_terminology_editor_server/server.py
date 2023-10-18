import json
import os
import pathlib
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


def make_random_id() -> str:
    return f"{random.randint(0, 2**31 - 1):08x}"


def load_jsonl(path: pathlib.Path) -> List[Any]:
    with path.open("r") as f:
        return [json.loads(line) for line in f.readlines()]


def load_all_term_records(term_dir: pathlib.Path) -> List[Dict]:
    records = []
    for jsonl_path in sorted(term_dir.glob("*.jsonl")):
        records.extend(load_jsonl(jsonl_path))
    return records


def pack_term_records(term_dir: pathlib.Path) -> None:
    table = {}

    for jsonl_path in sorted(term_dir.glob("*.jsonl")):
        key = int(jsonl_path.stem) // 60 // 60 * 60 * 60
        if key in table:
            table[key].append(jsonl_path)
        else:
            table[key] = [jsonl_path]

    for key, jsonl_paths in table.items():
        records = []
        for jsonl_path in jsonl_paths:
            records.extend(load_jsonl(jsonl_path))
        records.sort(key=lambda r: r["updatedAt"])
        new_jsonl_path = term_dir / f"{str(key)}.jsonl"
        with new_jsonl_path.open("w") as f:
            for record in records:
                json.dump(record, f, sort_keys=True, ensure_ascii=False)
                print("", file=f)
        for jsonl_path in jsonl_paths:
            if jsonl_path != new_jsonl_path:
                jsonl_path.unlink()


class AddTerm(BaseModel):
    id: Optional[str]
    parentId: Optional[str]
    representativeJa: str
    representativeEn: Optional[str]


DATA_DIR = pathlib.Path(os.environ["DATA_DIR"])
TERM_DIR = DATA_DIR / "term"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    representatives = {"ja": body.representativeJa}
    if body.representativeEn is not None:
        representatives["en"] = body.representativeEn

    record = {
        "id": new_id,
        "parentId": body.parentId,
        "updatedAt": now,
        "representatives": representatives,
    }

    jsonl_path = TERM_DIR / f"{str(now)}.jsonl"
    print(jsonl_path)

    with jsonl_path.open("w") as f:
        json.dump(record, f, sort_keys=True, ensure_ascii=False)

    return record


@app.post("/term/pack")
def post_term_pack():
    pack_term_records(TERM_DIR)
    return {}
