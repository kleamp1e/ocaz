from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, List, Tuple

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .const import service
from .cv_util import get_video_properties, open_video_capture, read_frame
from .face_attribute_classifier import Age, Emotion, Race
from .face_detector import BoundingBox, Landmarks
from .face_extractor import FaceExtractor


@dataclass
class Face:
    faceIndex: int
    score: float
    boundingBox: BoundingBox
    landmarks: Landmarks
    emotion: Emotion
    age: Age
    female: float
    race: Race


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
                    face.score,
                    face.boundingBox.to_tuple(),
                    face.landmarks.to_tuple(),
                    face.emotion.to_tuple(),
                    face.age,
                    face.sex.female,
                    face.race.to_tuple(),
                    face.facenet512,
                )
            )

    return np.array(
        face_list,
        dtype=[
            ("frameIndex", np.uint32),
            ("faceIndex", np.uint32),
            ("score", np.float16),
            ("boundingBox", np.uint16, (4,)),  # x1, y1, x2, y2
            ("landmarks", np.float16, (5, 2)),  # x, y
            ("emotion", np.float16, (7,)),
            ("age", np.float16),
            ("female", np.float16),
            ("race", np.float16, (6,)),
            ("facenet512", np.float32, (512,)),
        ],
    )


def convert_faces_array_to_json(faces: np.ndarray) -> List[Face]:
    return [
        Face(
            faceIndex=int(faces["faceIndex"][f]),
            score=float(faces["score"][f]),
            boundingBox=BoundingBox.from_numpy(faces["boundingBox"][f]),
            landmarks=Landmarks.from_numpy(faces["landmarks"][f]),
            emotion=Emotion.from_numpy(faces["emotion"][f]),
            age=float(faces["age"][f]),
            female=float(faces["female"][f]),
            race=Race.from_numpy(faces["race"][f]),
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


face_extractor = FaceExtractor()

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


# @app.get("/detect", response_model=DetectResponse)
@app.get("/detect")
async def get_detect(url: str, frame_indexes: str = "0") -> Any:
    frame_indexes = sorted(list(set(map(lambda s: int(s), frame_indexes.split(",")))))

    with open_video_capture(url) as video_capture:
        video_properties = get_video_properties(video_capture)
        frame_faces_pairs = []
        for frame_index in frame_indexes:
            frame = read_frame(video_capture, frame_index=frame_index)
            faces = face_extractor.extract(frame)
            for face in faces:
                face_dict = asdict(face)
                del face_dict["alignedImage"]
                del face_dict["facenet512"]
                print(face_dict)
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
