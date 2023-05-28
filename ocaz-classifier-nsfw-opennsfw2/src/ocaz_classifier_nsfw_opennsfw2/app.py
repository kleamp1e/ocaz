import datetime
import hashlib
import io
from typing import Dict

import numpy as np
import opennsfw2
import PIL.Image
import PIL.ImageOps
import tensorflow as tf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

classification_model = opennsfw2.make_open_nsfw_model()

SERVICE = {
    "name": "ocaz-classifier-nsfw-opennsfw2",
    "version": version,
    "libraries": {
        "opennsfw2": opennsfw2.__version__,
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
    pil_image = pil_image.convert("RGB")
    image_width, image_height = pil_image.size

    np_image = opennsfw2.preprocess_image(pil_image)
    np_image = np.expand_dims(np_image, axis=0)

    result = classification_model.predict(np_image)

    return {
        "service": SERVICE,
        "time": datetime.datetime.now().timestamp(),
        "image": {
            "size": len(image_bin),
            "width": image_width,
            "height": image_height,
            "sha1": hashlib.sha1(image_bin).hexdigest(),
        },
        "labels": {
            "sfw": float(result[0][0]),
            "nsfw": float(result[0][1]),
        },
    }
