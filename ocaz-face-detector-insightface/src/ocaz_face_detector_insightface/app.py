from datetime import datetime
from typing import Any, Dict, List

import insightface
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import version
from .cv_util import get_video_properties, open_video_capture, read_frame
from .face_detector import FaceDetector


def convert_faces_to_numpy(faces: List[Any]) -> np.ndarray:
    return np.array(
        [
            (
                face.det_score,
                face.bbox,
                face.kps,
                face.landmark_2d_106,
                face.landmark_3d_68,
                face.pose,
                {"M": 0, "F": 1}[face.sex],
                face.age,
                face.normed_embedding,
            )
            for face in faces
        ],
        dtype=[
            ("score", np.float16),
            ("boundingBox", np.float16, (4,)),  # x1, y1, x2, y2
            ("keyPoints", np.float16, (5, 2)),  # x, y
            ("landmark2d106", np.float16, (106, 2)),  # x, y
            ("landmark3d68", np.float16, (68, 3)),  # x, y, z
            ("pose", np.float16, (3,)),  # pitch, yaw, roll
            ("female", np.uint8),
            ("age", np.uint8),
            ("normedEmbedding", np.float32, (512,)),
        ],
    )


face_detector = FaceDetector()

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
    "libraries": {"insightface": insightface.__version__},
}


class Service(BaseModel):
    name: str
    version: str
    libraries: Dict[str, str]


class AboutResponse(BaseModel):
    service: Service
    time: float


@app.get("/about", response_model=AboutResponse)
async def get_about() -> Any:
    return {
        "service": SERVICE,
        "time": datetime.now().timestamp(),
    }


@app.get("/detect")
async def get_detect(url: str) -> Any:
    with open_video_capture(url) as video_capture:
        video_properties = get_video_properties(video_capture)
        frame = read_frame(video_capture)

    faces = face_detector.detect(frame)
    # print(faces)
    numpy_faces = convert_faces_to_numpy(faces)
    print(numpy_faces)

    return {
        "service": SERVICE,
        "time": datetime.now().timestamp(),
        "request": {"url": url, "width": video_properties.width, "height": video_properties.height},
        "result": {},
    }
