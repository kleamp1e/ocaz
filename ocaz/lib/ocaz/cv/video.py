from typing import Any, Dict

import cv2


class VideoCaptureOpener:
    def __init__(self, url: str):
        self.url = url

    def __enter__(self):
        self.video_capture = cv2.VideoCapture(self.url)
        assert self.video_capture.isOpened()
        return self.video_capture

    def __exit__(self, exc_type, exc_value, traceback):
        self.video_capture.release()


def get_video_info(video_capture: cv2.VideoCapture) -> Dict:
    return {
        "width": int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "numberOfFrames": int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        "fps": video_capture.get(cv2.CAP_PROP_FPS),
    }


def read_frame(video_capture: cv2.VideoCapture, frame_index: int) -> Any:
    assert video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = video_capture.read()
    assert ret
    return frame
