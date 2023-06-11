from dataclasses import dataclass
from typing import NewType

import cv2
import numpy as np
from deepface import DeepFace
from deepface.extendedmodels import Age, Emotion, Gender, Race
from retinaface import RetinaFace
from retinaface.commons import postprocess


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
        assert image.shape == (48, 48)  # H,W
        assert image.dtype == np.float32

        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
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


class FaceFeatureExtractorFacenet512:
    def __init__(self) -> None:
        self.model = DeepFace.build_model("Facenet512")

    def extract(self, image: np.ndarray) -> np.ndarray:
        assert image.shape == (160, 160, 3)  # H,W,C(BGR)
        assert image.dtype == np.float32
        return self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]


class RetinaFaceDetector:
    def __init__(self):
        RetinaFace.build_model()

    # https://github.com/serengil/retinaface/blob/878a1f6c5fa38227aa19b9881f1169b361563615/retinaface/RetinaFace.py#L182
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

        results.sort(key=lambda f: f["score"])

        return results


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
