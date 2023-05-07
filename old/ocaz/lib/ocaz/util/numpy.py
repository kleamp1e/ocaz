from typing import Dict
import pathlib

import numpy as np


def save_npz(path: pathlib.Path, data: Dict, compressed: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.parent / ("~" + path.name)
    if compressed:
        np.savez_compressed(temp_path, **data)
    else:
        np.savez(temp_path, **data)
    temp_path.rename(path)
