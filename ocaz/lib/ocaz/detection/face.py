from typing import Dict, List, Tuple
import hashlib
import math

import insightface
import numpy as np


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
                video_info["numberOfFrames"],
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


def make_numpy_dict(object_id: str, video_info: Dict, frame_faces: List[Tuple]) -> Dict:
    return {
        "videos": make_videos(object_id, video_info),
        "frames": make_frames(object_id, frame_faces),
        "faces": make_faces(object_id, frame_faces),
    }
