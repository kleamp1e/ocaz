import contextlib
from datetime import datetime
from typing import Any, Dict, List

import cv2
import insightface
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import version


@contextlib.contextmanager
def open_video_capture(path: str) -> cv2.VideoCapture:
    video_capture = cv2.VideoCapture(path)
    assert video_capture.isOpened()
    try:
        yield video_capture
    finally:
        video_capture.release()


def get_video_properties(video_capture: cv2.VideoCapture) -> Dict[str, Any]:
    return {
        "width": int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "numberOfFrames": int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        "fps": video_capture.get(cv2.CAP_PROP_FPS),
    }


def read_frame(video_capture: cv2.VideoCapture, frame_index: int = None) -> np.ndarray:
    if frame_index:
        assert video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = video_capture.read()
    assert ret
    return frame


class FaceDetector:
    def __init__(self, providers=["CUDAExecutionProvider"]):
        self.face_analysis = insightface.app.FaceAnalysis(
            providers=providers,
        )
        self.face_analysis.prepare(ctx_id=0, det_size=(640, 640))

    def detect(self, image):
        height, width = image.shape[:2]
        if width < 640 and height < 640:
            new_image = np.zeros((640, 640, 3), dtype=np.uint8)
            new_image[0:height, 0:width] = image
            image = new_image
        return self.face_analysis.get(image)


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
async def get_about():
    return {
        "service": SERVICE,
        "time": datetime.now().timestamp(),
    }


@app.get("/detect")
async def get_detect(url: str):
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
        "request": {"url": url, "width": video_properties["width"], "height": video_properties["height"]},
        "result": {},
    }
