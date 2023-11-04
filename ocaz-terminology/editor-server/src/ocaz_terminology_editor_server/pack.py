import json
import os
from functools import reduce
from pathlib import Path

import click


def load_jsonl(path: Path) -> list[any]:
    with path.open("r") as f:
        return [json.loads(line) for line in f.readlines()]


def load_fragments(dir_path: Path) -> list[any]:
    records = []
    for jsonl_path in sorted(dir_path.glob("*.jsonl")):
        records.extend(load_jsonl(jsonl_path))
    return records


def make_id_fragments_table(fragments: list[any]) -> dict[str, list[any]]:
    table = {}
    for fragment in fragments:
        id = fragment["id"]
        items = table.get(id, [])
        items.append(fragment)
        table[id] = sorted(items, key=lambda x: x["updatedAt"])
    return table


def make_merged_records(id_fragments_table: dict[str, list[any]]) -> list[any]:
    def union(a: dict, b: dict) -> dict:
        return a | b

    records = [
        reduce(union, fragments, {"createdAt": fragments[0]["updatedAt"]})
        for _id, fragments in id_fragments_table.items()
    ]
    records.sort(key=lambda x: x["id"])
    return records


def save_jsonl(path: Path, records: list[any]) -> None:
    with path.open("w") as f:
        for record in records:
            json.dump(record, f, sort_keys=True, ensure_ascii=False)
            print("", file=f)


@click.command()
@click.option(
    "-f",
    "--fragment-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=os.environ.get("FRAGMENT_DIR", None),
)
@click.option("-o", "--output-jsonl", required=True, type=click.Path(file_okay=True, dir_okay=False, writable=True))
def main(fragment_dir: str, output_jsonl: str) -> None:
    fragment_dir_path = Path(fragment_dir).resolve()
    output_jsonl_path = Path(output_jsonl).resolve()

    fragments = load_fragments(fragment_dir_path)
    id_fragments_table = make_id_fragments_table(fragments)
    records = make_merged_records(id_fragments_table)
    save_jsonl(output_jsonl_path, records)


if __name__ == "__main__":
    main()
