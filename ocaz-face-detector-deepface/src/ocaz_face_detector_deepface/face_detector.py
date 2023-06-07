import cv2
import numpy as np
from deepface import DeepFace
from deepface.commons import functions
from deepface.extendedmodels import Age, Emotion, Gender, Race


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
