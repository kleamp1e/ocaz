# FROM nvidia/cuda:11.0.3-cudnn8-devel-ubuntu20.04
FROM nvidia/cuda:11.4.3-cudnn8-runtime-ubuntu20.04
# FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu22.04
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
  && rm --recursive --force /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip setuptools

ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
ENV PATH=/opt/poetry/bin:${PATH}

WORKDIR /opt/app
ENV HOME=/opt/app
COPY pyproject.toml poetry.lock ${HOME}/
RUN poetry install --no-root
COPY ./model/buffalo_l.zip ${HOME}/.insightface/models/
# TODO: マージする。
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    unzip \
  && rm --recursive --force /var/lib/apt/lists/*
RUN cd ${HOME}/.insightface/models/ \
  && unzip -d buffalo_l buffalo_l.zip \
  && rm buffalo_l.zip
