import re

import cv2
import numpy as np
from retinaface import RetinaFace
from retinaface.commons import postprocess


# https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/commons/functions.py#L119
def resize(image: np.ndarray, width: int, height: int) -> np.ndarray:
    image_height, image_width, _ = face_image.shape
    factor = min(height / image_height, width / image_width)
    resized_image = cv2.resize(
        image,
        (
            int(image_width * factor),
            int(image_height * factor),
        ),
    )
    assert resized_image.shape[0] <= height
    assert resized_image.shape[1] <= width
    return resized_image


# https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/commons/functions.py#L119
def pad(image: np.ndarray, width: int, height: int) -> np.ndarray:
    assert image.shape[0] <= height
    assert image.shape[1] <= width
    image_height, image_width, _ = image.shape
    diff_h = height - image_height
    diff_w = width - image_width
    padded_image = np.pad(
        image,
        (
            (diff_h // 2, diff_h - diff_h // 2),
            (diff_w // 2, diff_w - diff_w // 2),
            (0, 0),
        ),
        "constant",
    )
    assert padded_image.shape[0] == height
    assert padded_image.shape[1] == width
    return padded_image


def resize_with_pad(image: np.ndarray, width: int, height: int) -> np.ndarray:
    return pad(resize(image, width, height), width, height)


class RetinaFaceDetector:
    def __init__(self):
        RetinaFace.build_model()

    def detect(self, image, threshold=0.5, allow_upscaling=True):
        def array_to_dict(x, y):
            return {"x": x, "y": y}

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
                {
                    "score": face["score"],
                    "boundingBox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    "landmarks": {
                        "leftEye": array_to_dict(*left_eye),
                        "rightEye": array_to_dict(*right_eye),
                        "nose": array_to_dict(*nose),
                        "mouthRight": array_to_dict(*mouth_right),
                        "mouthLeft": array_to_dict(*mouth_left),
                    },
                    "alignedImage": aligned_image,
                }
            )

        return results


image = cv2.imread("image1.jpg")

# resp = RetinaFace.detect_faces(image, threshold=0.5)
# print(resp)

face_detector = RetinaFaceDetector()
faces = face_detector.detect(image)
for i, face in enumerate(faces):
    aligned_image = face["alignedImage"]
    cv2.imwrite(f"face_{i}.jpg", aligned_image)

    # print(faces)

# resp = RetinaFace.extract_faces(image, threshold=0.5)
# print(resp[0].shape)
# print(resp[0].dtype)
# cv2.imwrite("face1.jpg", resp[0][:, :, ::-1])


# face_image = resp[0]

# resized_image = resize(face_image, 224, 224)
# print(resized_image.shape)
# cv2.imwrite("face1_resized.jpg", resized_image[:, :, ::-1])
# padded_image = pad(resized_image, 224, 224)
# print(padded_image.shape)
# cv2.imwrite("face1_padded.jpg", padded_image[:, :, ::-1])

# rp_image = resize_with_pad(face_image, 224, 224)
# print(rp_image.shape)
# cv2.imwrite("face1_rp.jpg", rp_image[:, :, ::-1])
