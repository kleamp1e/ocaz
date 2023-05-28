import numpy as np
import opennsfw2

model = opennsfw2.make_open_nsfw_model()
model.predict(np.zeros((1, 224, 224, 3), dtype=np.uint8))
