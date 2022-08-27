#!/usr/bin/env python3

import logging
from typing import Dict
import math

import click
import cv2
import numpy as np


class VideoCaptureOpener:
    def __init__(self, url):
        self.url = url

    def __enter__(self):
        self.video_capture = cv2.VideoCapture(self.url)
        assert self.video_capture.isOpened()
        return self.video_capture

    def __exit__(self, exc_type, exc_value, traceback):
        self.video_capture.release()


def get_video_info(video_capture) -> Dict:
    return {
        "width": int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "n_frames": int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        "fps": video_capture.get(cv2.CAP_PROP_FPS),
    }


def select_frames(
    n_frames: int,
    fps: float,
    max_frames_per_second: float,
    max_frames_per_video: int,
):
    n_selected_frames = sorted(
        [1, math.floor(n_frames / fps * max_frames_per_second), max_frames_per_video]
    )[1]
    return np.unique(
        np.linspace(
            0, n_frames - 1, n_selected_frames + 1, endpoint=False, dtype=np.uint32
        )[1:]
    ).tolist()


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

    with VideoCaptureOpener(url) as video_capture:
        video_info = get_video_info(video_capture)
        logging.debug("video_info = %s", video_info)
        selected_frame_indexes = select_frames(
            n_frames=video_info["n_frames"],
            fps=video_info["fps"],
            max_frames_per_second=max_frames_per_second,
            max_frames_per_video=max_frames_per_video,
        )
        logging.debug("selected_frame_indexes = %s", selected_frame_indexes)


if __name__ == "__main__":
    main()
