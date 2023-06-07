import cv2
import numpy as np
from deepface import DeepFace
from deepface.extendedmodels import Age, Emotion, Gender, Race


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class EmotionClassifier:
    def __init__(self):
        self.model = DeepFace.build_model("Emotion")

    def predict(self, image):
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
    def __init__(self):
        self.model = DeepFace.build_model("Age")

    def predict(self, image):
        assert image.shape == (224, 224, 3)  # BGR
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        return Age.findApparentAge(predictions)


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class SexClassifier:
    def __init__(self):
        self.model = DeepFace.build_model("Gender")

    def predict(self, image):
        assert image.shape == (224, 224, 3)  # BGR
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return {label: predictions[i] / sum for i, label in enumerate(Gender.labels)}


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class RaceClassifier:
    def __init__(self):
        self.model = DeepFace.build_model("Race")

    def predict(self, image):
        assert image.shape == (224, 224, 3)  # BGR
        assert image.dtype == np.float32
        predictions = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        sum = predictions.sum()
        return {label: predictions[i] / sum for i, label in enumerate(Race.labels)}
