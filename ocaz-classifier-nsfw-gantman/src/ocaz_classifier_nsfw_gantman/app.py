import datetime
import hashlib
import io
import os
from typing import Dict

import nsfw_detector.predict
import numpy as np
import PIL.Image
import PIL.ImageOps
import tensorflow as tf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tensorflow import keras

from . import version

for physical_device in tf.config.experimental.list_physical_devices("GPU"):
    tf.config.experimental.set_memory_growth(physical_device, True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

classification_model = nsfw_detector.predict.load_model(os.environ["GANTMAN_MODEL_DIR"])

SERVICE = {
    "name": "ocaz-classifier-nsfw-gantman",
    "version": version,
    "libraries": {
        "nsfw_detector": "1.2.0",
    },
}


class Service(BaseModel):
    name: str
    version: str
    libraries: Dict[str, str]


class Image(BaseModel):
    size: int
    width: int
    height: int
    sha1: str


class AboutResponse(BaseModel):
    service: Service
    time: float


class ClassifyResponse(BaseModel):
    service: Service
    time: float
    image: Image
    labels: Dict[str, float]


@app.get("/about", response_model=AboutResponse)
async def get_about():
    return {
        "service": SERVICE,
        "time": datetime.datetime.now().timestamp(),
    }


@app.post("/classify", response_model=ClassifyResponse)
async def post_classify(file: UploadFile = File(...)):
    if not file.content_type in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="File format not supported.")

    image_bin = await file.read()

    pil_image = PIL.Image.open(io.BytesIO(image_bin))
    pil_image = PIL.ImageOps.exif_transpose(pil_image)
    image_width, image_height = pil_image.size

    image_dim = nsfw_detector.predict.IMAGE_DIM
    pil_image = keras.utils.load_img(
        io.BytesIO(image_bin), target_size=(image_dim, image_dim)
    )
    np_image = keras.preprocessing.image.img_to_array(pil_image)
    np_image /= 255
    np_image = np.expand_dims(np_image, axis=0)

    result = nsfw_detector.predict.classify_nd(classification_model, np_image)

    return {
        "service": SERVICE,
        "time": datetime.datetime.now().timestamp(),
        "image": {
            "size": len(image_bin),
            "width": image_width,
            "height": image_height,
            "sha1": hashlib.sha1(image_bin).hexdigest(),
        },
        "labels": result[0],
    }
