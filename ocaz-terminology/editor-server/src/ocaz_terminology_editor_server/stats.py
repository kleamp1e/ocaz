import os
from pathlib import Path

import click

from .pack import load_fragments, make_id_fragments_table, make_merged_records


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

    representatives = {}
    synonyms = {}
    for record in records:
        for lang in record["representatives"].keys():
            representatives[lang] = representatives.get(lang, 0) + 1
        for synonym in record.get("synonyms", []):
            for lang in synonym.keys():
                synonyms[lang] = synonyms.get(lang, 0) + 1

    print(f"terms: {len(records)}")
    print("  representatives:")
    for lang in sorted(representatives.keys()):
        print(f"    {lang}: {representatives[lang]}")
    print("  synonyms:")
    for lang in sorted(synonyms.keys()):
        print(f"    {lang}: {synonyms[lang]}")


if __name__ == "__main__":
    main()
