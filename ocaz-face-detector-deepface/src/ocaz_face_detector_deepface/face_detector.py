from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from retinaface import RetinaFace
from retinaface.commons import postprocess


@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class Vector2:
    x: float
    y: float

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Landmarks:
    leftEye: Vector2
    rightEye: Vector2
    nose: Vector2
    mouthRight: Vector2
    mouthLeft: Vector2


class RetinaFaceDetector:
    @dataclass
    class Result:
        score: float
        boundingBox: BoundingBox
        landmarks: Landmarks
        alignedImage: np.ndarray

    def __init__(self):
        RetinaFace.build_model()

    # https://github.com/serengil/retinaface/blob/878a1f6c5fa38227aa19b9881f1169b361563615/retinaface/RetinaFace.py#L182
    def detect(self, image: np.ndarray, threshold: float = 0.5, allow_upscaling: bool = True) -> List[Result]:
        def to_vector2(x: np.float32, y: np.float32):
            return Vector2(x=float(x), y=float(y))

        faces = RetinaFace.detect_faces(image, threshold=threshold, allow_upscaling=allow_upscaling)

        results = []
        for _, face in faces.items():
            x1, y1, x2, y2 = face["facial_area"]
            face_image = image[y1:y2, x1:x2]

            landmarks = face["landmarks"]
            left_eye = landmarks["left_eye"]
            right_eye = landmarks["right_eye"]
            nose = landmarks["nose"]
            mouth_right = landmarks["mouth_right"]
            mouth_left = landmarks["mouth_left"]

            aligned_image = postprocess.alignment_procedure(face_image, right_eye, left_eye, nose)

            results.append(
                self.Result(
                    score=float(face["score"]),
                    boundingBox=BoundingBox(x1=int(x1), y1=int(y1), x2=int(x2), y2=int(y2)),
                    landmarks=Landmarks(
                        leftEye=to_vector2(*left_eye),
                        rightEye=to_vector2(*right_eye),
                        nose=to_vector2(*nose),
                        mouthRight=to_vector2(*mouth_right),
                        mouthLeft=to_vector2(*mouth_left),
                    ),
                    alignedImage=aligned_image,
                )
            )

        results.sort(key=lambda f: f.score)

        return results
