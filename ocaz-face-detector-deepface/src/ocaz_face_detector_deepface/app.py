import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

import cv2
import numpy as np
from deepface import DeepFace
from deepface.commons import functions
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .const import service
from .cv_util import get_video_properties, open_video_capture, read_frame
from .face_detector import (
    AgeEstimator,
    CombinedClassifier,
    EmotionClassifier,
    FaceFeatureExtractorFacenet512,
    RaceClassifier,
    RetinaFaceDetector,
    SexClassifier,
    resize_with_pad,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

combined_classifier = CombinedClassifier()
face_feature_extractor = FaceFeatureExtractorFacenet512()

face_detector = RetinaFaceDetector()
emotion_classifier = EmotionClassifier()
age_estimator = AgeEstimator()
sex_classifier = SexClassifier()
race_classifier = RaceClassifier()

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

        face_48x48_gray = resize_with_pad(aligned_image, 48, 48)
        face_48x48_gray = cv2.cvtColor(face_48x48_gray, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"face_{i}_48x48.jpg", face_48x48_gray)
        face_48x48_gray = face_48x48_gray.astype(np.float32) / 255
        emotion = emotion_classifier.predict(face_48x48_gray)
        print(emotion)

        face_224x224_bgr = resize_with_pad(aligned_image, 224, 224)
        cv2.imwrite(f"face_{i}_224x224.jpg", face_224x224_bgr)
        face_224x224_bgr = face_224x224_bgr.astype(np.float32) / 255

        age = age_estimator.predict(face_224x224_bgr)
        print(age)
        sex = sex_classifier.predict(face_224x224_bgr)
        print(sex)
        race = (race_classifier.predict(face_224x224_bgr),)
        print(race)

        # del face["alignedImage"]
        print(face)
        # print(json.dumps(asdict(face), indent=1))

    """
    model_name = "Facenet512"
    detector_backend = "retinaface"

    print(frame.shape)
    # print(frame)
    # cv2.imwrite("frame.jpg", frame)

    target_size = functions.find_target_size(model_name=model_name)
    # target_size = (224, 224)
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
    print(len(img_objs))

    model = DeepFace.build_model(model_name)
    print(model)
    print(str(type(model)))

    for img_content, img_region, confidence in img_objs:
        print((img_content.shape, img_region, confidence))
        # cv2.imwrite("img_content.jpg", (img_content[0] * 255).astype(np.uint8))
        # if img_content.shape[0] > 0 and img_content.shape[1] > 0:
        # prediction = combined_classifier.predict(img_content[0])
        # print(json.dumps(asdict(prediction)))
        # print(json.dumps(asdict(prediction.emotion)))
        # print(json.dumps(prediction.age))
        # print(json.dumps(asdict(prediction.sex)))
        # print(json.dumps(asdict(prediction.race)))
        # embedding = model.predict(img_content, verbose=0)[0]
        embedding = face_feature_extractor.extract(img_content[0])
        print(embedding)
        print(embedding.shape)
        print(embedding.dtype)
    """

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
