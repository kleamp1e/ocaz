from dataclasses import dataclass
from typing import List

import numpy as np

from .face_attribute_classifier import Age, CombinedClassifier, Emotion, Race, Sex
from .face_detector import BoundingBox, Landmarks, RetinaFaceDetector


class FaceExtractor:
    @dataclass
    class Result:
        score: float
        boundingBox: BoundingBox
        landmarks: Landmarks
        alignedImage: np.ndarray
        emotion: Emotion
        age: Age
        sex: Sex
        race: Race
        facenet512: np.ndarray

    def __init__(self):
        self.face_detector = RetinaFaceDetector()
        self.combined_classifier = CombinedClassifier()

    def extract(self, image: np.ndarray) -> List[Result]:
        faces = self.face_detector.detect(image)

        results = []
        for face in faces:
            attribute = self.combined_classifier.predict(face.alignedImage)
            results.append(
                self.Result(
                    score=face.score,
                    boundingBox=face.boundingBox,
                    landmarks=face.landmarks,
                    alignedImage=face.alignedImage,
                    emotion=attribute.emotion,
                    age=attribute.age,
                    sex=attribute.sex,
                    race=attribute.race,
                    facenet512=attribute.facenet512,
                )
            )

        return results
