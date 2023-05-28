FROM nvcr.io/nvidia/tensorflow:23.03-tf2-py3
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    libopencv-dev \
    unzip \
    wget \
  && rm --recursive --force /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip
WORKDIR /opt/app
RUN wget --quiet https://github.com/GantMan/nsfw_model/releases/download/1.1.0/nsfw_mobilenet_v2_140_224.zip \
  && unzip nsfw_mobilenet_v2_140_224.zip \
  && rm nsfw_mobilenet_v2_140_224.zip
ENV GANTMAN_MODEL_DIR /opt/app/mobilenet_v2_140_224
COPY pyproject.toml ./
COPY src/ ./src/
RUN python3 -m pip install --editable .
ENV LANG C.UTF-8
ENV TZ Asia/Tokyo
EXPOSE 8000
CMD ["uvicorn", "--host=0.0.0.0", "--port=8000", "ocaz_classifier_nsfw_gantman.app:app"]
