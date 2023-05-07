#!/usr/bin/env python3

import logging
import os
import pathlib
import sys

import click

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "lib"))
from ocaz.detection.face import (
    FaceDetector,
    sample_frames,
    detect_face,
    make_numpy_dict,
    make_numpy_path,
)
from ocaz.meta import make_meta_json_path
from ocaz.util.json import load_json
from ocaz.util.numpy import save_npz


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

    frame_indexes = sample_frames(
        n_frames=meta_info["numberOfFrames"],
        fps=meta_info["fps"],
        max_frames_per_second=max_frames_per_second,
        max_frames_per_video=max_frames_per_video,
    )
    logging.debug("frame_indexes = %s", frame_indexes)

    frame_faces = detect_face(
        face_detector=face_detector,
        url=meta_info["url"],
        frame_indexes=frame_indexes,
    )
    logging.debug("frame_faces.len = %s", len(frame_faces))

    numpy_dict = make_numpy_dict(
        object_id=object_id, video_info=meta_info, frame_faces=frame_faces
    )

    numpy_path = make_numpy_path(data_dir, object_id)
    save_npz(
        path=numpy_path,
        data=numpy_dict,
        compressed=True,
    )
    logging.info("numpy_path = %s", numpy_path)

    logging.info("done")


if __name__ == "__main__":
    main()
