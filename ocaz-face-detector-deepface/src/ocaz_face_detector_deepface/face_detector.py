from dataclasses import dataclass
from typing import NewType

import cv2
import numpy as np
from deepface import DeepFace
from deepface.extendedmodels import Age, Emotion, Gender, Race


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class EmotionClassifier:
    @dataclass
    class Result:
        angry: float
        disgust: float
        fear: float
        happy: float
        sad: float
        surprise: float
        neutral: float

    def __init__(self) -> None:
        self.model = DeepFace.build_model("Emotion")

    def predict(self, image: np.ndarray) -> Result:
        assert image.shape == (224, 224, 3)  # H,W,C(BGR)
        assert image.dtype == np.float32

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_gray = cv2.resize(image_gray, (48, 48))
        assert image_gray.shape == (48, 48)  # H,W

        predictions = self.model.predict(np.expand_dims(image_gray, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return self.Result(**{label: float(predictions[i] / sum) for i, label in enumerate(Emotion.labels)})


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class AgeEstimator:
    Result = NewType("Result", float)

    def __init__(self) -> None:
        self.model = DeepFace.build_model("Age")

    def predict(self, image: np.ndarray) -> Result:
        assert image.shape == (224, 224, 3)  # H,W,C(BGR)
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        return Age.findApparentAge(predictions)


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class SexClassifier:
    @dataclass
    class Result:
        male: float
        female: float

    def __init__(self) -> None:
        self.model = DeepFace.build_model("Gender")
        self.table = {"Man": "male", "Woman": "female"}

    def predict(self, image: np.ndarray) -> Result:
        assert image.shape == (224, 224, 3)  # H,W,C(BGR)
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return self.Result(**{self.table[label]: float(predictions[i] / sum) for i, label in enumerate(Gender.labels)})


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class RaceClassifier:
    @dataclass
    class Result:
        asian: float
        indian: float
        black: float
        white: float
        middleEastern: float
        latinoHispanic: float

    def __init__(self) -> None:
        self.model = DeepFace.build_model("Race")
        self.table = {
            "asian": "asian",
            "indian": "indian",
            "black": "black",
            "white": "white",
            "middle eastern": "middleEastern",
            "latino hispanic": "latinoHispanic",
        }

    def predict(self, image: np.ndarray) -> Result:
        assert image.shape == (224, 224, 3)  # H,W,C(BGR)
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return self.Result(**{self.table[label]: float(predictions[i] / sum) for i, label in enumerate(Race.labels)})


class CombinedClassifier:
    @dataclass
    class Result:
        emotion: EmotionClassifier.Result
        age: AgeEstimator.Result
        sex: SexClassifier.Result
        race: RaceClassifier.Result

    def __init__(self) -> None:
        self.emotion_classifier = EmotionClassifier()
        self.age_estimator = AgeEstimator()
        self.sex_classifier = SexClassifier()
        self.race_classifier = RaceClassifier()

    def predict(self, image: np.ndarray) -> Result:
        assert image.shape == (224, 224, 3)  # H,W,C(BGR)
        assert image.dtype == np.float32
        return self.Result(
            emotion=self.emotion_classifier.predict(image),
            age=self.age_estimator.predict(image),
            sex=self.sex_classifier.predict(image),
            race=self.race_classifier.predict(image),
        )
