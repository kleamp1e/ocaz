# ocaz-sandbox

```sh
cd ~/repo/github.com/kleamp1e/ocaz/sandbox/
docker-compose build
docker-compose up -d
```

## mongo-express

http://localhost:27002/

## sandbox

```sh
docker-compose build sandbox
docker-compose run --rm --user $(id -u):$(id -g) --env HOME=/tmp/home sandbox

# in container:

export PATH=${PATH}:${HOME}/.local/bin
python3 -m pip install --editable .[dev]

pysen run lint
pysen run format

python3 -m ocaz_sandbox.scan_nginx --help
python3 -m ocaz_sandbox.scan_nginx http://localhost:8000/ > url.txt
python3 -m ocaz_sandbox.make_index --help
python3 -m ocaz_sandbox.add_url --help
cat url.txt | python3 -m ocaz_sandbox.add_url --stdin
python3 -m ocaz_sandbox.resolve_object_meta --help
python3 -m ocaz_sandbox.resolve_object_meta --max-records 1
python3 -m ocaz_sandbox.resolve_media_meta --help
python3 -m ocaz_sandbox.resolve_media_meta
python3 -m ocaz_sandbox.resolve_sha1 --help
python3 -m ocaz_sandbox.resolve_phash --help
python3 -m ocaz_sandbox.stats --help
python3 -m ocaz_sandbox.predict_nsfw_opennsfw2 --help
python3 -m ocaz_sandbox.predict_nsfw_gantman --help

uvicorn ocaz_sandbox.forwarder:app --host 0.0.0.0 --port 8000 --reload
```

## ocaz-forwarder

* http://localhost:27003/
* http://localhost:27003/url/sha1/{url_sha1}
* http://localhost:27003/object/head10mbSha1/{head_10mb_sha1}
* http://localhost:27003/object/sha1/{object_sha1}

```sh
docker-compose build ocaz-forwarder
docker-compose up -d ocaz-forwarder
docker-compose run --rm --service-ports --user $(id -u):$(id -g) --env HOME=/tmp/home --volume $(pwd)/../ocaz-sandbox:/mnt/workspace --workdir /mnt/workspace ocaz-forwarder bash

# in container:

export PATH=${PATH}:${HOME}/.local/bin
python3 -m pip install --editable .[dev]
uvicorn ocaz_sandbox.forwarder:app --host 0.0.0.0 --port 8000 --reload
```

## ocaz-video-digester

* http://localhost:27004/
* http://localhost:27004/processing
* http://localhost:27004/object/head10mbSha1/{head_10mb_sha1}

```sh
docker-compose build ocaz-video-digester
docker-compose up -d ocaz-video-digester
docker-compose run --rm --service-ports --user $(id -u):$(id -g) --env HOME=/tmp/home --volume $(pwd)/../ocaz-sandbox:/mnt/workspace --workdir /mnt/workspace ocaz-video-digester bash

# in container:

export PATH=${PATH}:${HOME}/.local/bin
python3 -m pip install --editable .[dev]
export OPENCV_VIDEOIO_DEBUG=1
export OPENCV_FFMPEG_DEBUG=1
export OPENCV_LOG_LEVEL=DEBUG
uvicorn ocaz_sandbox.video_digester:app --host 0.0.0.0 --port 8000 --reload
```

## ocaz-simple-browser

http://localhost:27004/

```sh
docker-compose build ocaz-simple-browser
docker-compose up -d ocaz-simple-browser
docker-compose run --rm --service-ports --volume $(pwd)/../ocaz-simple-browser:/mnt/workspace --workdir /mnt/workspace/app ocaz-simple-browser sh

# in container:

npm run dev
```

## ocaz-finder

* http://localhost:27006/docs
* http://localhost:27006/
* http://localhost:27006/query
* http://localhost:27006/find

```sh
docker-compose build ocaz-finder
docker-compose up -d ocaz-finder
docker-compose run --rm --service-ports --user $(id -u):$(id -g) --env HOME=/tmp/home --volume $(pwd)/../ocaz-finder:/mnt/workspace --workdir /mnt/workspace ocaz-finder bash

# in container:

export PATH=${PATH}:${HOME}/.local/bin
python3 -m pip install --editable .[dev]
uvicorn ocaz_finder.app:app --host 0.0.0.0 --port 8000 --reload
```

## ocaz-classifier-nsfw-opennsfw2

* http://localhost:27007/docs
* http://localhost:27007/about
* http://localhost:27007/classify

```sh
docker-compose build ocaz-classifier-nsfw-opennsfw2
docker-compose up -d ocaz-classifier-nsfw-opennsfw2
docker-compose run --rm --service-ports --user $(id -u):$(id -g) --env HOME=/tmp/home --volume $(pwd)/../ocaz-classifier-nsfw-opennsfw2:/mnt/workspace --workdir /mnt/workspace ocaz-classifier-nsfw-opennsfw2 bash

curl --request POST --header "Content-Type: multipart/form-data" --form "file=@test.jpg;type=image/jpeg" http://localhost:27007/classify

# in container:

export PATH=${PATH}:${HOME}/.local/bin
python3 -m pip install --editable .[dev]
uvicorn --host=0.0.0.0 --port=8000 --reload ocaz_classifier_nsfw_opennsfw2.app:app
```

## ocaz-classifier-nsfw-gantman

* http://localhost:27008/docs
* http://localhost:27008/about
* http://localhost:27008/classify

```sh
docker-compose build ocaz-classifier-nsfw-gantman
docker-compose up -d ocaz-classifier-nsfw-gantman
docker-compose run --rm --service-ports --user $(id -u):$(id -g) --env HOME=/tmp/home --volume $(pwd)/../ocaz-classifier-nsfw-gantman:/mnt/workspace --workdir /mnt/workspace ocaz-classifier-nsfw-gantman bash

curl --request POST --header "Content-Type: multipart/form-data" --form "file=@test.jpg;type=image/jpeg" http://localhost:27008/classify

# in container:

export PATH=${PATH}:${HOME}/.local/bin
python3 -m pip install --editable .[dev]
uvicorn --host=0.0.0.0 --port=8000 --reload ocaz_classifier_nsfw_gantman.app:app
```

## ocaz-face-detector-insightface

* http://localhost:27009/docs
* http://localhost:27009/about

```sh
docker-compose build ocaz-face-detector-insightface
docker-compose up -d ocaz-face-detector-insightface
docker-compose run --rm --service-ports --volume $(pwd)/../ocaz-face-detector-insightface:/mnt/workspace --workdir /mnt/workspace ocaz-face-detector-insightface bash

# in container:

python3 -m pip install --editable .[dev]
uvicorn --host=0.0.0.0 --port=8000 --reload ocaz_face_detector_insightface.app:app
```

## ocaz-face-detector-deepface

```sh
docker-compose build ocaz-face-detector-deepface
docker-compose up -d ocaz-face-detector-deepface
docker-compose run --rm --service-ports --volume $(pwd)/../ocaz-face-detector-deepface:/mnt/workspace --workdir /mnt/workspace ocaz-face-detector-deepface bash

# in container:

python3 -m pip install --editable .[dev]
uvicorn --host=0.0.0.0 --port=8000 --reload ocaz_face_detector_deepface.app:app
```
