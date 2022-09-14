#!/usr/bin/env python3

from typing import Any, Dict, List, Tuple
import hashlib
import logging
import math
import os
import pathlib
import sys

import click
import cv2
import insightface
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))
from ocaz.object_util import get_object_info
from ocaz.path_util import make_nested_id_path


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


def make_videos(object_id: str, video_info: Dict) -> np.ndarray:
    return np.array(
        [
            (
                object_id,
                video_info["width"],
                video_info["height"],
                video_info["n_frames"],
                video_info["fps"],
            )
        ],
        dtype=[
            ("objectId", "<U45"),
            ("width", np.uint16),
            ("height", np.uint16),
            ("numberOfFrames", np.uint32),
            ("fps", np.float16),
        ],
    )


def make_frames(object_id: str, frame_faces: List[Tuple]) -> np.ndarray:
    return np.array(
        [(object_id, frame_index, len(faces)) for frame_index, faces in frame_faces],
        dtype=[
            ("objectId", "<U45"),
            ("frameIndex", np.uint32),
            ("numberOfFaces", np.uint8),
        ],
    )


def make_face_id(object_id: str, frame_index: int, bbox: np.ndarray):
    parts = [object_id, frame_index]
    parts.extend(bbox.astype(np.int32).tolist())
    parts = map(lambda x: str(x), parts)
    parts = ",".join(parts)
    return hashlib.sha1(parts.encode("utf-8")).hexdigest()


def make_faces(object_id: str, frame_faces: List[Tuple]) -> np.ndarray:
    face_list = []
    for frame_index, faces in frame_faces:
        face_list.extend(
            [
                (
                    object_id,
                    frame_index,
                    make_face_id(object_id, frame_index, face.bbox),
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
            ]
        )

    return np.array(
        face_list,
        dtype=[
            ("objectId", "<U45"),
            ("frameIndex", np.uint32),
            ("faceId", "<U40"),
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


def save_npz(path: pathlib.Path, data: Dict, compressed: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.parent / ("~" + path.name)
    if compressed:
        np.savez_compressed(temp_path, **data)
    else:
        np.savez(temp_path, **data)
    temp_path.rename(path)


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
@click.option(
    "-d",
    "--data-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="data directory path",
)
@click.option("--max-frames-per-second", type=float, default=1.0)
@click.option("--max-frames-per-video", type=int, default=300)
@click.argument("url")
def main(
    log_level: str,
    data_dir: str,
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
    logging.debug("data_dir = %s", data_dir)

    object_info = get_object_info(url)
    object_id = object_info["object_id"]
    logging.debug("object_info = %s", object_info)
    logging.debug("object_id = %s", object_id)

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

    videos = make_videos(object_id, video_info)
    frames = make_frames(object_id, frame_faces)
    faces = make_faces(object_id, frame_faces)

    numpy_dir = pathlib.Path(data_dir) / "detection" / "face" / "v1"
    numpy_path = make_nested_id_path(numpy_dir, object_id, ".npz")
    save_npz(
        path=numpy_path,
        data={"videos": videos, "frames": frames, "faces": faces},
        compressed=True,
    )
    logging.info("numpy_path = %s", numpy_path)

    logging.info("done")


if __name__ == "__main__":
    main()
