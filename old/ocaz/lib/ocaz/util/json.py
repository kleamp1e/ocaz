from typing import Any
import json
import pathlib


def save_json(path: pathlib.Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.parent / ("~" + path.name)
    with temp_path.open("w") as file:
        json.dump(data, file, sort_keys=True, ensure_ascii=False, indent=1)
    temp_path.rename(path)


def load_json(path: pathlib.Path) -> Any:
    with path.open("r") as file:
        return json.load(file)
