import re

import cv2
import numpy as np
from ocaz_face_detector_deepface.face_detector import RetinaFaceDetector


# https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/commons/functions.py#L119
def resize(image: np.ndarray, width: int, height: int) -> np.ndarray:
    image_height, image_width, _ = image.shape
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


image = cv2.imread("image1.jpg")

face_detector = RetinaFaceDetector()
faces = face_detector.detect(image)
for i, face in enumerate(faces):
    aligned_image = face["alignedImage"]
    cv2.imwrite(f"face_{i}.jpg", aligned_image)

    del face["alignedImage"]
    print(face)

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
