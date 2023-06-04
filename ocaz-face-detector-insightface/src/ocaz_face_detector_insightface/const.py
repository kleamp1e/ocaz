import insightface

from . import name, version

service = {
    "name": name,
    "version": version,
    "libraries": {"insightface": insightface.__version__},
}
