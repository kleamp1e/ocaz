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


def make_jsonl_path(term_dir: pathlib.Path, current_time: datetime) -> pathlib.Path:
    return term_dir / f"{str(int(current_time.timestamp() * 1000))}.jsonl"


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
        key = int(jsonl_path.stem) // 1000 // 60 // 60 * 60 * 60 * 1000
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
            table[record["id"]].update(record)
        else:
            table[record["id"]] = record
    return {"terms": sorted(list(table.values()), key=lambda r: r["id"])}


class AddTerm(BaseModel):
    id: Optional[str]
    parentId: Optional[str]
    representativeJa: str
    representativeEn: Optional[str]


@app.post("/term/add")
def post_term_add(body: AddTerm):
    new_id = body.id if body.id is not None else make_random_id()
    now = datetime.now().timestamp()
    representatives = {"ja": body.representativeJa}
    if body.representativeEn is not None:
        representatives["en"] = body.representativeEn

    record = {
        "id": new_id,
        "parentId": body.parentId,
        "updatedAt": now,
        "representatives": representatives,
    }

    jsonl_path = TERM_DIR / f"{str(int(now * 1000))}.jsonl"
    print(jsonl_path)

    with jsonl_path.open("w") as f:
        json.dump(record, f, sort_keys=True, ensure_ascii=False)

    return record


class Synonym(BaseModel):
    ja: str
    en: Optional[str]


class SetSynonyms(BaseModel):
    synonyms: List[Synonym]


@app.post("/term/id/{id}/synonyms")
def post_term_id_synonyms(id: str, body: SetSynonyms):
    now = datetime.now()
    jsonl_path = make_jsonl_path(term_dir=TERM_DIR, current_time=now)

    record = {
        "id": id,
        "updatedAt": now.timestamp(),
        "synonyms": [{k: v for k, v in dict(synonym).items() if v is not None} for synonym in body.synonyms],
    }

    with jsonl_path.open("w") as f:
        json.dump(record, f, sort_keys=True, ensure_ascii=False)

    return record


@app.post("/term/pack")
def post_term_pack():
    pack_term_records(TERM_DIR)
    return {}
