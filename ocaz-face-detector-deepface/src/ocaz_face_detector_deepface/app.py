import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .const import service
from .cv_util import get_video_properties, open_video_capture, read_frame
from .face_attribute_classifier import Age, CombinedClassifier, Emotion, Race, Sex
from .face_detector import BoundingBox, Landmarks, RetinaFaceDetector


@dataclass
class Face:
    score: float
    boundingBox: BoundingBox
    landmarks: Landmarks
    alignedImage: np.ndarray
    emotion: Emotion
    age: Age
    sex: Sex
    race: Race
    facenet512: np.ndarray


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

face_detector = RetinaFaceDetector()
combined_classifier = CombinedClassifier()


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
        # frame_faces_pairs = []
        for frame_index in frame_indexes:
            frame = read_frame(video_capture, frame_index=frame_index)
        #     faces = face_detector.detect(frame)
        #     frame_faces_pairs.append((frame_index, faces))

    # frames_array = convert_to_frames_array(frame_faces_pairs)
    # faces_array = convert_to_faces_array(frame_faces_pairs)

    faces = face_detector.detect(frame)
    for i, face in enumerate(faces):
        aligned_image = face.alignedImage
        print(aligned_image.shape)

        result = combined_classifier.predict(aligned_image)
        # print(result)

        ret = Face(
            score=face.score,
            boundingBox=face.boundingBox,
            landmarks=face.landmarks,
            alignedImage=face.alignedImage,
            emotion=result.emotion,
            age=result.age,
            sex=result.sex,
            race=result.race,
            facenet512=result.facenet512,
        )
        ret = asdict(ret)
        del ret["alignedImage"]
        del ret["facenet512"]
        print(ret)
        # print(json.dumps(face, indent=1))

    return {
        "service": service,
        "time": datetime.now().timestamp(),
        "request": {
            "url": url,
            "frameIndexes": frame_indexes,
        },
        # "result": {
        #     "video": video_properties,
        #     "frames": convert_frames_array_to_json(frames_array, faces_array),
        # },
    }
