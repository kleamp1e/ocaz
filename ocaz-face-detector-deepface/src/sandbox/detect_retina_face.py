import cv2
from ocaz_face_detector_deepface.face_detector import RetinaFaceDetector, resize_with_pad

image = cv2.imread("image1.jpg")

face_detector = RetinaFaceDetector()
faces = face_detector.detect(image)
for i, face in enumerate(faces):
    aligned_image = face["alignedImage"]
    print(aligned_image.shape)
    cv2.imwrite(f"face_{i}.jpg", aligned_image)

    resized_image = resize_with_pad(aligned_image, 224, 224)
    print(resized_image.shape)
    cv2.imwrite(f"face_{i}_resize.jpg", resized_image)

    del face["alignedImage"]
    print(face)

# rp_image = resize_with_pad(face_image, 224, 224)
# print(rp_image.shape)
# cv2.imwrite("face1_rp.jpg", rp_image[:, :, ::-1])
