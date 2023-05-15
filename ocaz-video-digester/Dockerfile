FROM ubuntu:22.04
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    build-essential \
    ca-certificates \
    ffmpeg \
    libmagic1 \
    libopencv-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
  && rm --recursive --force /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip
WORKDIR /opt/app
COPY pyproject.toml ./
COPY src/ ./src/
RUN python3 -m pip install --editable .[dev]
CMD uvicorn ocaz_sandbox.video_digester:app --host 0.0.0.0 --port 8000
