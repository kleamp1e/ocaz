import pathlib

from .util.path import make_nested_id_path


def make_meta_json_path(data_dir: pathlib.Path, object_id: str) -> pathlib.Path:
    meta_dir = pathlib.Path(data_dir) / "meta" / "v1"
    return make_nested_id_path(meta_dir, object_id, ".json")
