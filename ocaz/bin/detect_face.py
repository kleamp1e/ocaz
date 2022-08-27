#!/usr/bin/env python3

from typing import Any, Dict, List
import logging
import math

import click
import cv2
import insightface
import numpy as np


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
        "n_frames": int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        "fps": video_capture.get(cv2.CAP_PROP_FPS),
    }


def read_frame(video_capture: cv2.VideoCapture, frame_index: int) -> Any:
    assert video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = video_capture.read()
    assert ret
    return frame


def sample_frames(
    n_frames: int,
    fps: float,
    max_frames_per_second: float,
    max_frames_per_video: int,
) -> List[int]:
    n_samples = sorted(
        [1, math.floor(n_frames / fps * max_frames_per_second), max_frames_per_video]
    )[1]
    return np.unique(
        np.linspace(0, n_frames - 1, n_samples + 1, endpoint=False, dtype=np.uint32)[1:]
    ).tolist()


class FaceDetector:
    def __init__(self, use_gpu: bool):
        if use_gpu:
            providers = ["CUDAExecutionProvider"]
        else:
            providers = ["CPUExecutionProvider"]
        self.face_analysis = insightface.app.FaceAnalysis(providers=providers)
        self.face_analysis.prepare(ctx_id=0, det_size=(640, 640))

    def detect(self, image):
        height, width = image.shape[:2]
        if width < 640 and height < 640:
            new_image = np.zeros((640, 640, 3), dtype=np.uint8)
            new_image[0:height, 0:width] = image
            image = new_image
        return self.face_analysis.get(image)


@click.command()
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(["info", "debug"]),
    default="info",
    help="log level",
)
@click.option("-d", "--db-dir", type=click.Path(), help="database directory path")
@click.option("--max-frames-per-second", type=float, default=1.0)
@click.option("--max-frames-per-video", type=int, default=300)
@click.argument("url")
def main(
    log_level: str,
    db_dir: str,
    max_frames_per_second: float,
    max_frames_per_video: int,
    url: str,
) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    logging.info("log_level = %s", log_level)
    logging.debug("url = %s", url)
    logging.debug("db_dir = %s", db_dir)

    face_detector = FaceDetector(use_gpu=True)

    with VideoCaptureOpener(url) as video_capture:
        video_info = get_video_info(video_capture)
        logging.debug("video_info = %s", video_info)

        sampled_frame_indexes = sample_frames(
            n_frames=video_info["n_frames"],
            fps=video_info["fps"],
            max_frames_per_second=max_frames_per_second,
            max_frames_per_video=max_frames_per_video,
        )
        logging.debug("sampled_frame_indexes = %s", sampled_frame_indexes)

        frame_faces = []
        for frame_index in sampled_frame_indexes:
            logging.info("frame_index = %s", frame_index)
            frame = read_frame(video_capture, frame_index)
            faces = face_detector.detect(frame)
            frame_faces.append((frame_index, faces))


if __name__ == "__main__":
    main()
