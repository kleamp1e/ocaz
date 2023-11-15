import os
from pathlib import Path

import click

from .pack import load_fragments, make_id_fragments_table, make_merged_records


def make_id_record_table(records: list[dict]) -> dict[str, dict]:
    return {record["id"]: record for record in records}


def make_id_nested_record_table(id_record_table: dict[str, dict]) -> dict[str, list[dict]]:
    table = {}  # dict[str, list[dict]]
    for record in id_record_table.values():
        nested = []
        current = record
        while True:
            nested.append(current)
            if current["parentId"] is None:
                break
            current = id_record_table[current["parentId"]]
        table[record["id"]] = nested
    return table


@click.command()
@click.option(
    "-f",
    "--fragment-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=os.environ.get("FRAGMENT_DIR", None),
)
@click.option("-c", "--count", required=True, type=int, default=10)
@click.option("-s", "--skip", required=True, type=int, default=0)
def main(fragment_dir: str, count: int, skip: int) -> None:
    fragment_dir_path = Path(fragment_dir).resolve()

    fragments = load_fragments(fragment_dir_path)
    id_fragments_table = make_id_fragments_table(fragments)
    records = make_merged_records(id_fragments_table)
    id_record_table = make_id_record_table(records)
    id_nested_record_table = make_id_nested_record_table(id_record_table)

    output = []
    for id, nested_record in id_nested_record_table.items():
        if "en" in nested_record[0]["representatives"]:
            # print(f"skip: [{id}] has already en")
            continue
        path = " > ".join(map(lambda r: r["representatives"]["ja"], reversed(nested_record[0:3])))
        output.append((id, "representatives", path))
        if len(output) >= count + skip:
            break

    for id, type, path in output[skip:]:
        print(f"{id}\t{type}\t{path}")


if __name__ == "__main__":
    main()
