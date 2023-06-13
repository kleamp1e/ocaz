FROM nvcr.io/nvidia/tensorflow:23.01-tf2-py3
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    libopencv-dev \
  && rm --recursive --force /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip~=23.1.2
WORKDIR /opt/app
COPY pyproject.toml ./
COPY src/ ./src/
RUN python3 -m pip install --editable .
ENV LANG C.UTF-8
ENV TZ Asia/Tokyo
EXPOSE 8000
CMD uvicorn --host=0.0.0.0 --port=8000 ocaz_face_detector_deepface.app:app
