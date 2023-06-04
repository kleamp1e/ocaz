from datetime import datetime
from typing import Any, Dict, List

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .const import service
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


def convert_numpy_faces_to_json(faces: np.ndarray) -> Dict:
    return [
        {
            "score": float(faces["score"][f]),
            "boundingBox": {
                "x1": float(faces["boundingBox"][f][0]),
                "y1": float(faces["boundingBox"][f][1]),
                "x2": float(faces["boundingBox"][f][2]),
                "y2": float(faces["boundingBox"][f][3]),
            },
            "keyPoints": [
                {
                    "x": float(faces["keyPoints"][f][kp][0]),
                    "y": float(faces["keyPoints"][f][kp][1]),
                }
                for kp in range(len(faces["keyPoints"][f]))
            ],
            "landmark2d106": [
                {
                    "x": float(faces["landmark2d106"][f][lm][0]),
                    "y": float(faces["landmark2d106"][f][lm][1]),
                }
                for lm in range(len(faces["landmark2d106"][f]))
            ],
            "landmark3d68": [
                {
                    "x": float(faces["landmark3d68"][f][lm][0]),
                    "y": float(faces["landmark3d68"][f][lm][1]),
                    "z": float(faces["landmark3d68"][f][lm][2]),
                }
                for lm in range(len(faces["landmark3d68"][f]))
            ],
            "pose": {
                "pitch": float(faces["pose"][f][0]),
                "yaw": float(faces["pose"][f][1]),
                "roll": float(faces["pose"][f][2]),
            },
            "female": int(faces["female"][f]),
            "age": int(faces["age"][f]),
        }
        for f in range(len(faces))
    ]


face_detector = FaceDetector()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        "service": service,
        "time": datetime.now().timestamp(),
    }


@app.get("/detect")
async def get_detect(url: str) -> Any:
    with open_video_capture(url) as video_capture:
        video_properties = get_video_properties(video_capture)
        frame = read_frame(video_capture)

    faces = face_detector.detect(frame)
    numpy_faces = convert_faces_to_numpy(faces)
    print(numpy_faces)
    json_faces = convert_numpy_faces_to_json(numpy_faces)
    print(json_faces)

    return {
        "service": service,
        "time": datetime.now().timestamp(),
        "request": {"url": url, "width": video_properties.width, "height": video_properties.height},
        "result": {"faces": json_faces},
    }
