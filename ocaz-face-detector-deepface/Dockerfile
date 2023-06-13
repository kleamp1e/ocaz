FROM ubuntu:22.04 as model
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    ca-certificates \
    wget \
  && rm --recursive --force /var/lib/apt/lists/*
RUN mkdir --parents /root/.deepface/weights \
  && cd /root/.deepface/weights/ \
  && wget https://github.com/serengil/deepface_models/releases/download/v1.0/retinaface.h5 \
  && wget https://github.com/serengil/deepface_models/releases/download/v1.0/facial_expression_model_weights.h5 \
  && wget https://github.com/serengil/deepface_models/releases/download/v1.0/age_model_weights.h5 \
  && wget https://github.com/serengil/deepface_models/releases/download/v1.0/gender_model_weights.h5 \
  && wget https://github.com/serengil/deepface_models/releases/download/v1.0/race_model_single_batch.h5 \
  && wget https://github.com/serengil/deepface_models/releases/download/v1.0/facenet512_weights.h5

FROM nvcr.io/nvidia/tensorflow:23.01-tf2-py3
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    libopencv-dev \
  && rm --recursive --force /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip~=23.1.2
COPY --from=model /root/.deepface/weights /root/.deepface/weights
WORKDIR /opt/app
COPY pyproject.toml ./
COPY src/ ./src/
RUN python3 -m pip install --editable .
ENV LANG C.UTF-8
ENV TZ Asia/Tokyo
EXPOSE 8000
CMD uvicorn --host=0.0.0.0 --port=8000 ocaz_face_detector_deepface.app:app
