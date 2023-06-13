import contextlib
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np


@contextlib.contextmanager
def open_video_capture(path: str) -> cv2.VideoCapture:
    video_capture = cv2.VideoCapture(path)
    assert video_capture.isOpened()
    try:
        yield video_capture
    finally:
        video_capture.release()


@dataclass
class VideoProperties:
    width: int
    height: int
    numberOfFrames: int
    fps: float


def get_video_properties(video_capture: cv2.VideoCapture) -> VideoProperties:
    return VideoProperties(
        width=int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        height=int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        numberOfFrames=int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        fps=video_capture.get(cv2.CAP_PROP_FPS),
    )


def read_frame(video_capture: cv2.VideoCapture, frame_index: Optional[int] = None) -> np.ndarray:
    if frame_index:
        assert video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = video_capture.read()
    assert ret
    return frame
