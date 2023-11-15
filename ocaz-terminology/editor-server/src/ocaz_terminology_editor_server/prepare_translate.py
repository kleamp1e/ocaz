import os
from pathlib import Path

import click

from .pack import load_fragments, make_id_fragments_table, make_merged_records


def make_id_record_table(records: list[dict]) -> dict[str, dict]:
    return {record["id"]: record for record in records}


def make_id_nested_record_table(id_record_table: dict[str, dict]) -> dict[str, list[dict]]:
    table = {}  # dict[str, list[dict]]
    for record in id_record_table.values():
        items = []
        current = record
        items.append(current)
        while current["parentId"] is not None:
            current = id_record_table[current["parentId"]]
            items.append(current)
        table[record["id"]] = items
    return table


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
    id_nested_record_table = make_id_nested_record_table(id_record_table)
    print(id_nested_record_table)


if __name__ == "__main__":
    main()
