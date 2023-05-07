from typing import Dict
import logging
import pathlib

from .cv.video import VideoCaptureOpener, get_video_info
from .util.object import get_object_info
from .util.path import make_nested_id_path


def make_meta_json_path(data_dir: pathlib.Path, object_id: str) -> pathlib.Path:
    meta_dir = data_dir / "meta" / "v1"
    return make_nested_id_path(meta_dir, object_id, ".json")


def get_meta_info(url: str) -> Dict:
    object_info = get_object_info(url)
    logging.debug("object_info = %s", object_info)

    with VideoCaptureOpener(url) as video_capture:
        video_info = get_video_info(video_capture)
        logging.debug("video_info = %s", video_info)

    return {
        "url": url,
        "size": object_info["contentLength"],
        "mimeType": object_info["contentType"],
        "objectId": object_info["objectId"],
        "width": video_info["width"],
        "height": video_info["height"],
        "numberOfFrames": video_info["numberOfFrames"],
        "fps": video_info["fps"],
    }
