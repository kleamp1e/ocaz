from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deepface.commons import functions

from .const import service
from .cv_util import VideoProperties, get_video_properties, open_video_capture, read_frame

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
        print(video_properties)
        # frame_faces_pairs = []
        for frame_index in frame_indexes:
            frame = read_frame(video_capture, frame_index=frame_index)
        #     faces = face_detector.detect(frame)
        #     frame_faces_pairs.append((frame_index, faces))

    # frames_array = convert_to_frames_array(frame_faces_pairs)
    # faces_array = convert_to_faces_array(frame_faces_pairs)

    model_name="Facenet512"
    detector_backend="retinaface"

    target_size = functions.find_target_size(model_name=model_name)
    print(target_size)

    img1_objs = functions.extract_faces(
        img=frame,
        target_size=target_size,
        detector_backend=detector_backend,
        grayscale=False,
        enforce_detection=False,
        align=False,
    )
    print(img1_objs)

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
