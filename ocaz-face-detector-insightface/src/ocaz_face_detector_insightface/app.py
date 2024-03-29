from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .const import service
from .cv_util import VideoProperties, get_video_properties, open_video_capture, read_frame
from .face_detector import FaceDetector


@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class Vector2:
    x: float
    y: float


@dataclass
class Vector3:
    x: float
    y: float
    z: float


@dataclass
class Pose:
    pitch: float
    yaw: float
    roll: float


@dataclass
class Face:
    faceIndex: int
    score: float
    boundingBox: BoundingBox
    keyPoints: List[Vector2]
    landmark2d106: List[Vector2]
    landmark3d68: List[Vector3]
    pose: Pose
    female: float
    age: float


@dataclass
class Frame:
    frameIndex: int
    faces: List[Face]


def convert_to_frames_array(frame_faces_pairs: List[Tuple[int, Any]]) -> np.ndarray:
    return np.array(
        [(frame_index, len(faces)) for frame_index, faces in frame_faces_pairs],
        dtype=[
            ("frameIndex", np.uint32),
            ("numberOfFaces", np.uint16),
        ],
    )


def convert_to_faces_array(frame_faces_pairs: List[Tuple[int, Any]]) -> np.ndarray:
    face_list = []

    for frame_index, faces in frame_faces_pairs:
        for face_index, face in enumerate(faces):
            face_list.append(
                (
                    frame_index,
                    face_index,
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
            )

    return np.array(
        face_list,
        dtype=[
            ("frameIndex", np.uint32),
            ("faceIndex", np.uint32),
            ("score", np.float16),
            ("boundingBox", np.float16, (4,)),  # x1, y1, x2, y2
            ("keyPoints", np.float16, (5, 2)),  # x, y
            ("landmark2d106", np.float16, (106, 2)),  # x, y
            ("landmark3d68", np.float16, (68, 3)),  # x, y, z
            ("pose", np.float16, (3,)),  # pitch, yaw, roll
            ("female", np.float16),
            ("age", np.float16),
            ("normedEmbedding", np.float32, (512,)),
        ],
    )


def convert_faces_array_to_json(faces: np.ndarray) -> List[Face]:
    return [
        Face(
            faceIndex=int(faces["faceIndex"][f]),
            score=float(faces["score"][f]),
            boundingBox=BoundingBox(
                x1=float(faces["boundingBox"][f][0]),
                y1=float(faces["boundingBox"][f][1]),
                x2=float(faces["boundingBox"][f][2]),
                y2=float(faces["boundingBox"][f][3]),
            ),
            keyPoints=[
                Vector2(
                    x=float(faces["keyPoints"][f][kp][0]),
                    y=float(faces["keyPoints"][f][kp][1]),
                )
                for kp in range(len(faces["keyPoints"][f]))
            ],
            landmark2d106=[
                Vector2(
                    x=float(faces["landmark2d106"][f][lm][0]),
                    y=float(faces["landmark2d106"][f][lm][1]),
                )
                for lm in range(len(faces["landmark2d106"][f]))
            ],
            landmark3d68=[
                Vector3(
                    x=float(faces["landmark3d68"][f][lm][0]),
                    y=float(faces["landmark3d68"][f][lm][1]),
                    z=float(faces["landmark3d68"][f][lm][2]),
                )
                for lm in range(len(faces["landmark3d68"][f]))
            ],
            pose=Pose(
                pitch=float(faces["pose"][f][0]),
                yaw=float(faces["pose"][f][1]),
                roll=float(faces["pose"][f][2]),
            ),
            female=float(faces["female"][f]),
            age=float(faces["age"][f]),
        )
        for f in range(len(faces))
    ]


def convert_frames_array_to_json(frames: np.ndarray, faces: np.ndarray) -> List[Frame]:
    return [
        Frame(
            frameIndex=int(frame_index),
            faces=convert_faces_array_to_json(faces[faces["frameIndex"] == frame_index]),
        )
        for frame_index in sorted(list(frames["frameIndex"]))
    ]


class Service(BaseModel):
    name: str
    version: str
    libraries: Dict[str, str]


class AboutResponse(BaseModel):
    service: Service
    time: float


class DetectResponseRequest(BaseModel):
    url: str
    frameIndexes: List[int]


class DetectResponseResult(BaseModel):
    video: VideoProperties
    frames: List[Frame]


class DetectResponse(BaseModel):
    service: Service
    time: float
    request: DetectResponseRequest
    result: DetectResponseResult

face_detector = FaceDetector()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/about", response_model=AboutResponse)
async def get_about() -> Any:
    return {
        "service": service,
        "time": datetime.now().timestamp(),
    }


@app.get("/detect", response_model=DetectResponse)
async def get_detect(url: str, frame_indexes: str = "0") -> Any:
    frame_indexes = sorted(list(set(map(lambda s: int(s), frame_indexes.split(",")))))

    with open_video_capture(url) as video_capture:
        video_properties = get_video_properties(video_capture)
        frame_faces_pairs = []
        for frame_index in frame_indexes:
            frame = read_frame(video_capture, frame_index=frame_index)
            faces = face_detector.detect(frame)
            frame_faces_pairs.append((frame_index, faces))

    frames_array = convert_to_frames_array(frame_faces_pairs)
    faces_array = convert_to_faces_array(frame_faces_pairs)

    return {
        "service": service,
        "time": datetime.now().timestamp(),
        "request": {
            "url": url,
            "frameIndexes": frame_indexes,
        },
        "result": {
            "video": video_properties,
            "frames": convert_frames_array_to_json(frames_array, faces_array),
        },
    }
