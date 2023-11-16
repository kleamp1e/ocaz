import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import click

from .pack import load_fragments, make_id_fragments_table, make_merged_records
from .prepare_translate import make_id_record_table


@click.command()
@click.option(
    "-f",
    "--fragment-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=os.environ.get("FRAGMENT_DIR", None),
)
def main(fragment_dir: str) -> None:
    fragment_dir_path = Path(fragment_dir).resolve()

    fragments = load_fragments(fragment_dir_path)
    id_fragments_table = make_id_fragments_table(fragments)
    records = make_merged_records(id_fragments_table)
    id_record_table = make_id_record_table(records)

    records = []
    for line in sys.stdin.readlines():
        id, type, ja_path, en_path, en1, en2, *_ = line.strip().split("\t") + [None]
        print((id, type, ja_path, en_path, en1, en2))

        if id not in id_record_table:
            print(f"skip: [{id}] is not found")
            continue
        if en2 == "-":
            print("skip: [{id}] was ignored")
            continue

        representatives = id_record_table[id]["representatives"].copy()
        representatives["en"] = en1 if en2 is None else en2
        if id_record_table[id]["representatives"] == representatives:
            print(f"skip: not changed -- {representatives}")
            continue

        record = {
            "id": id,
            "updatedAt": datetime.now().timestamp(),
            "representatives": representatives,
        }
        print(record)
        records.append(record)

        time.sleep(0.01)

    if len(records) <= 0:
        print("no records")
        return

    temp_jsonl_path = fragment_dir_path / f"~{int(datetime.now().timestamp() * 1000)}.jsonl"
    with temp_jsonl_path.open("w") as jsonl:
        for record in records:
            json.dump(record, jsonl, sort_keys=True, ensure_ascii=False)
            print("", file=jsonl)

    out_jsonl_path = fragment_dir_path / f"{int(datetime.now().timestamp() * 1000)}.jsonl"
    temp_jsonl_path.rename(out_jsonl_path)
    print(out_jsonl_path)


if __name__ == "__main__":
    main()
