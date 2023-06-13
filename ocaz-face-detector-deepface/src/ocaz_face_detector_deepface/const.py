# import deepface

from . import name, version

service = {
    "name": name,
    "version": version,
    "libraries": {
        # "deepface": deepface.__version__,
        "deepface": "0.0.79",
    },
}
