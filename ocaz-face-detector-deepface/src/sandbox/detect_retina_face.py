import re

import cv2
import numpy as np
from retinaface import RetinaFace


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


image = cv2.imread("image1.jpg")

# resp = RetinaFace.detect_faces(image, threshold=0.5)
# print(resp)

# resp = RetinaFace.extract_faces(image, threshold=0.5)
faces = RetinaFace.detect_faces(image, threshold=0.5)
print(faces)
# print(resp[0].shape)
# print(resp[0].dtype)
# cv2.imwrite("face1.jpg", resp[0][:, :, ::-1])

for key in faces.keys():
    print(key)
    face = faces[key]
    print(face)

    x1, y1, x2, y2 = face["facial_area"]
    print((x1, y1, x2, y2))

    facial_img = image[y1:y2, x1:x2]
    cv2.imwrite("face1.jpg", facial_img)

    result = {
        "score": face["score"],
    }
    print(result)

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
