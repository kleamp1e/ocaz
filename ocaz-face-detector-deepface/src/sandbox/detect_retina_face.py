from retinaface import RetinaFace
import cv2
import numpy as np

image = cv2.imread("image1.jpg")

# resp = RetinaFace.detect_faces(image, threshold=0.5)
# print(resp)

resp = RetinaFace.extract_faces(image, threshold=0.5)
# print(resp)
print(resp[0].shape)
print(resp[0].dtype)
cv2.imwrite("face1.jpg", resp[0][:, :, ::-1])

face_image=resp[0]

# https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/commons/functions.py#L119

target_size = (224, 224)
target_h, target_w = target_size
source_h, source_w, _ = face_image.shape
factor = min(target_h / source_h, target_w / source_w)
resized_image = cv2.resize(face_image, (
    int(source_w * factor),
    int(source_h * factor),
))
print(resized_image.shape)
cv2.imwrite("face1_resized.jpg", resized_image[:, :, ::-1])

resized_h, resized_w, _ = resized_image.shape
diff_h = target_h - resized_h
diff_w = target_w - resized_w
padded_image = np.pad(
    resized_image,
    (
        (diff_h // 2, diff_h - diff_h // 2),
        (diff_w // 2, diff_w - diff_w // 2),
        (0, 0),
    ),
    "constant",
)
print(padded_image.shape)
cv2.imwrite("face1_padded.jpg", padded_image[:, :, ::-1])
