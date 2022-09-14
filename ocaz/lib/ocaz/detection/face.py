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
