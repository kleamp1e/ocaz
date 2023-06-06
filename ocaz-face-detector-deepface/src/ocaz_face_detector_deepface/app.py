from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .const import service

# from .cv_util import VideoProperties, get_video_properties, open_video_capture, read_frame
# from .face_detector import FaceDetector

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/about", response_model=AboutResponse)
@app.get("/about")
async def get_about() -> Any:
    return {
        "service": service,
        "time": datetime.now().timestamp(),
    }
