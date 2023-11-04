import os
from pathlib import Path

import click


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


if __name__ == "__main__":
    main()
