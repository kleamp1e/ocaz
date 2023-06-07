from dataclasses import dataclass
from typing import Dict

import cv2
import numpy as np
from deepface import DeepFace
from deepface.extendedmodels import Age, Emotion, Gender, Race


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class EmotionClassifier:
    def __init__(self) -> None:
        self.model = DeepFace.build_model("Emotion")

    def predict(self, image: np.ndarray) -> Dict[str, float]:
        assert image.shape == (224, 224, 3)  # BGR
        assert image.dtype == np.float32

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_gray = cv2.resize(image_gray, (48, 48))
        assert image_gray.shape == (48, 48)

        predictions = self.model.predict(np.expand_dims(image_gray, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return {label: predictions[i] / sum for i, label in enumerate(Emotion.labels)}


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class AgeEstimator:
    def __init__(self) -> None:
        self.model = DeepFace.build_model("Age")

    def predict(self, image: np.ndarray) -> float:
        assert image.shape == (224, 224, 3)  # BGR
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        return Age.findApparentAge(predictions)


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class SexClassifier:
    def __init__(self) -> None:
        self.model = DeepFace.build_model("Gender")
        self.table = {"Man": "male", "Woman": "female"}

    def predict(self, image: np.ndarray) -> Dict[str, float]:
        assert image.shape == (224, 224, 3)  # BGR
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return {self.table[label]: predictions[i] / sum for i, label in enumerate(Gender.labels)}


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class RaceClassifier:
    def __init__(self) -> None:
        self.model = DeepFace.build_model("Race")

    def predict(self, image: np.ndarray) -> Dict[str, float]:
        assert image.shape == (224, 224, 3)  # BGR
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return {label.replace(" ", "_"): predictions[i] / sum for i, label in enumerate(Race.labels)}


class CombinedClassifier:
    @dataclass
    class Result:
        emotion: Dict
        age: float
        sex: Dict
        race: Dict

    def __init__(self) -> None:
        self.emotion_classifier = EmotionClassifier()
        self.age_estimator = AgeEstimator()
        self.sex_classifier = SexClassifier()
        self.race_classifier = RaceClassifier()

    def predict(self, image: np.ndarray) -> Result:
        assert image.shape == (224, 224, 3)  # BGR
        assert image.dtype == np.float32
        return self.Result(
            emotion=self.emotion_classifier.predict(image),
            age=self.age_estimator.predict(image),
            sex=self.sex_classifier.predict(image),
            race=self.race_classifier.predict(image),
        )
