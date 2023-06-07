from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from deepface import DeepFace
from deepface.commons import functions
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .const import service
from .cv_util import VideoProperties, get_video_properties, open_video_capture, read_frame
from .face_detector import AgeEstimator, EmotionClassifier, RaceClassifier, SexClassifier

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


emotion_classifier = EmotionClassifier()
age_estimator = AgeEstimator()
sex_classifier = SexClassifier()
race_classifier = RaceClassifier()


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

    model_name = "Facenet512"
    detector_backend = "retinaface"

    print(frame.shape)
    # print(frame)
    # cv2.imwrite("frame.jpg", frame)

    # target_size = functions.find_target_size(model_name=model_name)
    target_size = (224, 224)
    print(target_size)

    img_objs = functions.extract_faces(
        img=frame,
        target_size=target_size,
        detector_backend=detector_backend,
        grayscale=False,
        enforce_detection=False,
        align=True,
    )
    # print(img_objs)

    for img_content, img_region, confidence in img_objs:
        print((img_content.shape, img_region, confidence))
        # cv2.imwrite("img_content.jpg", (img_content[0] * 255).astype(np.uint8))
        if img_content.shape[0] > 0 and img_content.shape[1] > 0:
            # print(predict_emotion(models["emotion"], img_content))
            print(emotion_classifier.predict(img_content))
            print(age_estimator.predict(img_content))
            print(sex_classifier.predict(img_content))
            print(race_classifier.predict(img_content))

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
