FROM ubuntu:22.04 AS opencv
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    libavcodec-dev \
    libavformat-dev \
    libjpeg-dev \
    libpng-dev \
    libswscale-dev \
    libtbb-dev \
    libtiff-dev \
    libv4l-dev \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-setuptools \
    wget \
  && rm --recursive --force /var/lib/apt/lists/*
RUN pip3 install numpy~=1.24.3
ENV OPENCV_VERSION 4.7.0
RUN mkdir -p /tmp/opencv
RUN cd /tmp/opencv/ \
  && wget --quiet https://github.com/opencv/opencv/archive/refs/tags/${OPENCV_VERSION}.tar.gz
RUN cd /tmp/opencv/ \
  && tar zxfv ${OPENCV_VERSION}.tar.gz \
  && mkdir opencv-${OPENCV_VERSION}/build
RUN cd /tmp/opencv/opencv-4.7.0/build/ \
  && cmake \
    -D CMAKE_INSTALL_PREFIX=/opt/opencv \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D WITH_FFMPEG=ON \
    -D WITH_PYTHON=ON \
    -D BUILD_opencv_python2=OFF \
    -D BUILD_opencv_python3=ON \
    -D PYTHON_DEFAULT_EXECUTABLE=python3 \
    .. \
  && make -j $(nproc) \
  && make install

# FROM ubuntu:22.04
# RUN apt-get update \
#   && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
#     build-essential \
#     ca-certificates \
#     ffmpeg \
#     libmagic1 \
#     libopencv-dev \
#     python3-dev \
#     python3-pip \
#     python3-setuptools \
#   && rm --recursive --force /var/lib/apt/lists/*
# RUN python3 -m pip install --upgrade pip
# WORKDIR /opt/app
# COPY pyproject.toml ./
# COPY src/ ./src/
# RUN python3 -m pip install --editable .[dev]
# CMD uvicorn ocaz_sandbox.video_digester:app --host 0.0.0.0 --port 8000
