FROM nvcr.io/nvidia/tensorflow:23.03-tf2-py3
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    libopencv-dev \
  && rm --recursive --force /var/lib/apt/lists/*
WORKDIR /opt/app
COPY ./ ./
RUN python3 -m pip install .
RUN python3 -m ocaz.classifier.nsfw.opennsfw2.load_model
ENV LANG C.UTF-8
ENV TZ Asia/Tokyo
CMD ["uvicorn", "--host=0.0.0.0", "ocaz.classifier.nsfw.opennsfw2.main:app"]
