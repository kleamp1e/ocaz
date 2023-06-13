from dataclasses import asdict
from datetime import datetime
from typing import Any, List, Tuple

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .const import service
from .cv_util import get_video_properties, open_video_capture, read_frame
from .face_extractor import FaceExtractor

def convert_to_frames_array(frame_faces_pairs: List[Tuple[int, Any]]) -> np.ndarray:
    return np.array(
        [(frame_index, len(faces)) for frame_index, faces in frame_faces_pairs],
        dtype=[
            ("frameIndex", np.uint32),
            ("numberOfFaces", np.uint16),
        ],
    )

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
    print(frames_array)
    # faces_array = convert_to_faces_array(frame_faces_pairs)

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
