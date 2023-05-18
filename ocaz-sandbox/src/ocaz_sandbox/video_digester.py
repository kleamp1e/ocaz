import contextlib
import hashlib
import json
import math
import os
import pathlib
import re
from typing import Any, Dict, Optional

import cv2
import fastapi
import numpy as np
import pymongo
from fastapi.responses import FileResponse

from .db import COLLECTION_URL, get_database


def not_found() -> fastapi.HTTPException:
    return fastapi.HTTPException(status_code=404, detail="not found")


SHA1_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def is_sha1(sha1: str) -> bool:
    return SHA1_PATTERN.match(sha1) is not None


def get_url_from_head_10mb_sha1(mongodb: pymongo.database.Database, head_10mb_sha1: str) -> Optional[str]:
    if record := mongodb[COLLECTION_URL].find_one({"head10mbSha1": head_10mb_sha1, "available": True}, {"url": True}):
        return record["url"]
    else:
        return None


@contextlib.contextmanager
def open_video_capture(url: str) -> cv2.VideoCapture:
    video_capture = cv2.VideoCapture(url)
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


def extract_key_frame_indexes(number_of_frames, n_blocks):
    interval = number_of_frames / (n_blocks + 1)
    return [math.floor(interval * (i + 1)) for i in range(n_blocks)]


def expand_frame_indexes(key_frame_indexes, frames_per_block, number_of_frames):
    frame_indexes = set()

    for key_frame_index in key_frame_indexes:
        for n in range(frames_per_block):
            frame_index = math.floor(key_frame_index - frames_per_block / 2 + n)
            if 0 <= frame_index <= number_of_frames - 1:
                frame_indexes.add(frame_index)

    return sorted(list(frame_indexes))


def calc_output_size(width, height, max_size):
    if width > height:
        return (max_size, math.floor((height / width) * max_size))
    else:
        return (math.floor((width / height) * max_size), max_size)


def make_config_file(cache_dir: pathlib.Path, number_of_blocks: int, max_size: int) -> str:
    config = {
        "numberOfBlocks": number_of_blocks,
        "maxSize": max_size,
    }
    config_json = json.dumps(config, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    config_key = hashlib.sha1(config_json.encode("utf-8")).hexdigest()
    config_json_path = cache_dir / config_key / "config.json"
    config_json_path.parent.mkdir(parents=True, exist_ok=True)
    if not config_json_path.exists():
        with config_json_path.open("w") as file:
            file.write(config_json)

    return config_key


def make_nested_id_name(id: str, ext: str = "") -> str:
    return f"{id[0:2]}/{id[2:4]}/{id}{ext}"


def make_digest_video(input_url: str, output_path: str, output_temp_path: str, max_size: int, number_of_blocks: int):
    if output_path.exists() or output_temp_path.exists():
        return

    with open_video_capture(input_url) as video_capture:
        video_properties = get_video_properties(video_capture)
        output_width, output_height = calc_output_size(video_properties["width"], video_properties["height"], max_size)

        output_temp_path.parent.mkdir(parents=True, exist_ok=True)
        output_video = cv2.VideoWriter(
            str(output_temp_path),
            cv2.VideoWriter_fourcc(*"VP90"),
            video_properties["fps"],
            (output_width, output_height),
        )

        key_frame_indexes = extract_key_frame_indexes(
            number_of_frames=video_properties["numberOfFrames"], n_blocks=number_of_blocks
        )

        frame_indexes = expand_frame_indexes(
            key_frame_indexes=key_frame_indexes,
            frames_per_block=math.floor(video_properties["fps"]),
            number_of_frames=video_properties["numberOfFrames"],
        )

        for frame_index in frame_indexes:
            frame = read_frame(video_capture, frame_index)
            resized_frame = cv2.resize(frame, (output_width, output_height))
            output_video.write(resized_frame)

        output_video.release()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_temp_path.rename(output_path)


def make_processing_video(
    output_path: str,
    max_size: int,
    text_color=(255, 255, 255),
    background_color=(0, 0, 0),
    font_scale: float = 1.0,
    font_thickness: int = 2,
    fps: float = 1.0,
) -> None:
    width, height = calc_output_size(1920, 1080, max_size)
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "Processing"
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_x = int((width - text_size[0]) / 2)
    text_y = int((height + text_size[1]) / 2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_video = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"VP90"),
        fps,
        (width, height),
    )

    for i in range(4):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = background_color
        cv2.putText(frame, text + ("." * i), (text_x, text_y), font, font_scale, text_color, font_thickness)
        output_video.write(frame)

    output_video.release()


OCAZ_MONGODB_URL = os.environ["OCAZ_MONGODB_URL"]
CACHE_DIR = pathlib.Path(os.environ["CACHE_DIR"])

mongodb = get_database(OCAZ_MONGODB_URL)

app = fastapi.FastAPI()


@app.get("/")
def get_root() -> Any:
    return {}


@app.get("/object/head10mbSha1/{head_10mb_sha1}")
def get_object_head_10mb_sha1(
    background_tasks: fastapi.BackgroundTasks, head_10mb_sha1: str, number_of_blocks: int = 10, max_size: int = 300
) -> Any:
    config_key = make_config_file(cache_dir=CACHE_DIR, number_of_blocks=number_of_blocks, max_size=max_size)
    digest_video_path = CACHE_DIR / config_key / make_nested_id_name(head_10mb_sha1, ".webm")
    digest_video_temp_path = digest_video_path.parent / ("~" + digest_video_path.name)
    processing_video_path = CACHE_DIR / config_key / "processing.webm"

    if not processing_video_path.exists():
        make_processing_video(output_path=processing_video_path, max_size=max_size)

    if is_sha1(head_10mb_sha1) and (url := get_url_from_head_10mb_sha1(mongodb, head_10mb_sha1)):
        if digest_video_path.exists():
            return FileResponse(
                str(digest_video_path),
                media_type="video/webm",
                headers={"Content-Disposition": "inline"},
            )
        else:
            if not digest_video_temp_path.exists():
                background_tasks.add_task(
                    make_digest_video,
                    input_url=url,
                    output_path=digest_video_path,
                    output_temp_path=digest_video_temp_path,
                    max_size=max_size,
                    number_of_blocks=number_of_blocks,
                )

            return FileResponse(
                str(processing_video_path),
                media_type="video/webm",
                headers={"Content-Disposition": "inline"},
            )
    else:
        raise not_found()
