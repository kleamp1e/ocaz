
from typing import Any
import fastapi

app = fastapi.FastAPI()


@app.get("/")
def get_root() -> Any:
    return {}
