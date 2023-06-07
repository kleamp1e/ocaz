import cv2
import numpy as np
from deepface import DeepFace
from deepface.commons import functions
from deepface.extendedmodels import Age, Emotion, Gender, Race


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class EmotionClassifier:
    def __init__(self):
        self.model = DeepFace.build_model("Emotion")

    def predict(self, images):
        assert images.shape == (1, 224, 224, 3)

        images_gray = cv2.cvtColor(images[0], cv2.COLOR_BGR2GRAY)
        images_gray = cv2.resize(images_gray, (48, 48))
        images_gray = np.expand_dims(images_gray, axis=0)
        assert images_gray.shape == (1, 48, 48)

        predictions = self.model.predict(images_gray, verbose=0)[0]
        sum = predictions.sum()
        return {label: predictions[i] / sum for i, label in enumerate(Emotion.labels)}


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class AgeEstimator:
    def __init__(self):
        self.model = DeepFace.build_model("Age")

    def predict(self, images):
        assert images.shape == (1, 224, 224, 3)
        predictions = self.model.predict(images, verbose=0)[0]
        return Age.findApparentAge(predictions)


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class SexClassifier:
    def __init__(self):
        self.model = DeepFace.build_model("Gender")

    def predict(self, images):
        assert images.shape == (1, 224, 224, 3)
        predictions = self.model.predict(images, verbose=0)[0]
        sum = predictions.sum()
        return {label: predictions[i] / sum for i, label in enumerate(Gender.labels)}


# REF: https://github.com/serengil/deepface/blob/ce4e4f664b66c05e682de8c0913798da0420dae1/deepface/DeepFace.py#L230
class RaceClassifier:
    def __init__(self):
        self.model = DeepFace.build_model("Race")

    def predict(self, images):
        assert images.shape == (1, 224, 224, 3)
        predictions = self.model.predict(images, verbose=0)[0]
        sum = predictions.sum()
        return {label: predictions[i] / sum for i, label in enumerate(Race.labels)}
