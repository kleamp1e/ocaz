import json
import os
from pathlib import Path

import click


def load_jsonl(path: Path) -> list[any]:
    with path.open("r") as f:
        return [json.loads(line) for line in f.readlines()]


def load_fragments(dir_path: Path) -> list[any]:
    fragments = []
    for jsonl_path in sorted(dir_path.glob("*.jsonl")):
        fragments.extend(load_jsonl(jsonl_path))
    return fragments


def make_id_records_table(records: list[any]) -> dict[list[any]]:
    table = {}
    for record in records:
        id = record["id"]
        items = table.get(id, [])
        items.append(record)
        table[id] = items
    return table


@click.command()
@click.option(
    "-d",
    "--data-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=os.environ.get("DATA_DIR", None),
)
def main(data_dir: str) -> None:
    data_dir_path = Path(data_dir).resolve()
    term_dir_path = data_dir_path / "term"
    fragment_dir_path = term_dir_path / "fragment"

    records = load_fragments(fragment_dir_path)
    # print(records)

    table = make_id_records_table(records)
    # print(table)
    for id, records in table.items():
        if len(records) >= 2:
            print((id, records))


if __name__ == "__main__":
    main()
