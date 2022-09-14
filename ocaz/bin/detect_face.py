#!/usr/bin/env python3

import logging
import os
import pathlib
import sys

import click

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))
from ocaz.cv.video import VideoCaptureOpener, get_video_info, read_frame
from ocaz.detection.face import FaceDetector, sample_frames, make_numpy_dict
from ocaz.meta import make_meta_json_path
from ocaz.util.json import load_json
from ocaz.util.numpy import save_npz
from ocaz.util.object import get_object_info
from ocaz.util.path import make_nested_id_path


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
@click.argument("object_id")
def main(
    log_level: str,
    data_dir: str,
    max_frames_per_second: float,
    max_frames_per_video: int,
    object_id: str,
) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    logging.debug("log_level = %s", log_level)
    logging.debug("data_dir = %s", data_dir)
    logging.debug("object_id = %s", object_id)

    meta_json_path = make_meta_json_path(pathlib.Path(data_dir), object_id)
    logging.debug("meta_json_path = %s", meta_json_path)

    meta_info = load_json(meta_json_path)
    logging.debug("meta_info = %s", meta_info)

    face_detector = FaceDetector(use_gpu=True)

    with VideoCaptureOpener(meta_info["url"]) as video_capture:
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

    numpy_dict = make_numpy_dict(
        object_id=object_id, video_info=video_info, frame_faces=frame_faces
    )
    numpy_dir = pathlib.Path(data_dir) / "detection" / "face" / "v1"
    numpy_path = make_nested_id_path(numpy_dir, object_id, ".npz")
    save_npz(
        path=numpy_path,
        data=numpy_dict,
        compressed=True,
    )
    logging.info("numpy_path = %s", numpy_path)

    logging.info("done")


if __name__ == "__main__":
    main()
