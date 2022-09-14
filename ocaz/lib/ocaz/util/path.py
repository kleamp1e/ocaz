import pathlib


def make_nested_id_path(dir: pathlib.Path, id: str, ext: str = "") -> pathlib.Path:
    return dir / id[0:2] / id[2:4] / (id + ext)
