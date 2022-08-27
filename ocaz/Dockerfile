FROM nvidia/cuda:11.4.3-cudnn8-runtime-ubuntu20.04
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    libopenblas-base \
    libopencv-dev \
    pandoc \
    python3-dev \
    python3-pip \
    python3-setuptools \
    unzip \
  && rm --recursive --force /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip setuptools

RUN python3 -m pip install poetry
ENV POETRY_VIRTUALENVS_CREATE=false

ENV HOME=/opt/app
WORKDIR ${HOME}
COPY ./pyproject.toml ./poetry.lock ${HOME}/
RUN poetry install --no-root

COPY ./model/buffalo_l.zip ${HOME}/.insightface/models/
RUN cd ${HOME}/.insightface/models/ \
  && unzip -d buffalo_l buffalo_l.zip \
  && rm buffalo_l.zip
# RUN insightface-cli model.download buffalo_l
