from dataclasses import dataclass
from typing import NewType

import cv2
import numpy as np
from deepface import DeepFace
from deepface.extendedmodels import Age as AgeModel
from deepface.extendedmodels import Emotion as EmotionModel
from deepface.extendedmodels import Gender as GenderModel
from deepface.extendedmodels import Race as RaceModel

Age = NewType("Result", float)



@dataclass
class Emotion:
    angry: float
    disgust: float
    fear: float
    happy: float
    sad: float
    surprise: float
    neutral: float


@dataclass
class Sex:
    male: float
    female: float


@dataclass
class Race:
    asian: float
    indian: float
    black: float
    white: float
    middleEastern: float
    latinoHispanic: float


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class EmotionClassifier:
    def __init__(self) -> None:
        self.model = DeepFace.build_model("Emotion")

    def predict(self, image: np.ndarray) -> Emotion:
        assert image.shape == (48, 48)  # H,W
        assert image.dtype == np.float32

        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return Emotion(**{label: float(predictions[i] / sum) for i, label in enumerate(EmotionModel.labels)})


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class AgeEstimator:
    def __init__(self) -> None:
        self.model = DeepFace.build_model("Age")

    def predict(self, image: np.ndarray) -> Age:
        assert image.shape == (224, 224, 3)  # H,W,C(BGR)
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        return AgeModel.findApparentAge(predictions)


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class SexClassifier:
    def __init__(self) -> None:
        self.model = DeepFace.build_model("Gender")
        self.table = {"Man": "male", "Woman": "female"}

    def predict(self, image: np.ndarray) -> Sex:
        assert image.shape == (224, 224, 3)  # H,W,C(BGR)
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return Sex(**{self.table[label]: float(predictions[i] / sum) for i, label in enumerate(GenderModel.labels)})


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class RaceClassifier:
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

    def predict(self, image: np.ndarray) -> Race:
        assert image.shape == (224, 224, 3)  # H,W,C(BGR)
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return Race(**{self.table[label]: float(predictions[i] / sum) for i, label in enumerate(RaceModel.labels)})


class CombinedClassifier:
    @dataclass
    class Result:
        emotion: Emotion
        age: Age
        sex: Sex
        race: Race

    def __init__(self) -> None:
        self.emotion_classifier = EmotionClassifier()
        self.age_estimator = AgeEstimator()
        self.sex_classifier = SexClassifier()
        self.race_classifier = RaceClassifier()

    def predict(self, aligned_face_image: np.ndarray) -> Result:
        face_48x48_gray = resize_with_pad(aligned_face_image, 48, 48)
        face_48x48_gray = cv2.cvtColor(face_48x48_gray, cv2.COLOR_BGR2GRAY)
        face_48x48_gray = face_48x48_gray.astype(np.float32) / 255

        face_224x224_bgr = resize_with_pad(aligned_face_image, 224, 224)
        face_224x224_bgr = face_224x224_bgr.astype(np.float32) / 255

        return self.Result(
            emotion=self.emotion_classifier.predict(face_48x48_gray),
            age=self.age_estimator.predict(face_224x224_bgr),
            sex=self.sex_classifier.predict(face_224x224_bgr),
            race=self.race_classifier.predict(face_224x224_bgr),
        )

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
