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
    print(Path(data_dir).resolve())


if __name__ == "__main__":
    main()
