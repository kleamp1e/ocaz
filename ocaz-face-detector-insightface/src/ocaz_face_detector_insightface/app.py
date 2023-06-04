from datetime import datetime
from typing import Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import version

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE = {
    "name": "ocaz-face-detector-insightface",
    "version": version,
    "libraries": {
        # "opennsfw2": opennsfw2.__version__,
    },
}


class Service(BaseModel):
    name: str
    version: str
    libraries: Dict[str, str]


class AboutResponse(BaseModel):
    service: Service
    time: float


@app.get("/about", response_model=AboutResponse)
async def get_about():
    return {
        "service": SERVICE,
        "time": datetime.now().timestamp(),
    }
