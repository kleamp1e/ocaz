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
docker-compose run --rm --service-ports --user $(id -u):$(id -g) --env HOME=/tmp/home --volume ../ocaz-sandbox:/mnt/workspace --workdir /mnt/workspace ocaz-forwarder bash

# in container:

export PATH=${PATH}:${HOME}/.local/bin
python3 -m pip install --editable .[dev]
uvicorn ocaz_sandbox.forwarder:app --host 0.0.0.0 --port 8000 --reload
```

## ocaz-video-digester

* http://localhost:27004/
* http://localhost:27004/object/head10mbSha1/{head_10mb_sha1}

```sh
docker-compose build ocaz-video-digester
docker-compose up -d ocaz-video-digester
docker-compose run --rm --service-ports --user $(id -u):$(id -g) --env HOME=/tmp/home --volume ../ocaz-sandbox:/mnt/workspace --workdir /mnt/workspace ocaz-video-digester bash

# in container:

export PATH=${PATH}:${HOME}/.local/bin
python3 -m pip install --editable .[dev]
uvicorn ocaz_sandbox.video_digester:app --host 0.0.0.0 --port 8000 --reload
```

## ocaz-simple-browser

http://localhost:27004/

```sh
docker-compose build ocaz-simple-browser
docker-compose up -d ocaz-simple-browser
docker-compose run --rm --service-ports --volume ../ocaz-simple-browser:/mnt/workspace --workdir /mnt/workspace/app ocaz-simple-browser sh

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
docker-compose run --rm --service-ports --user $(id -u):$(id -g) --env HOME=/tmp/home --volume ../ocaz-finder:/mnt/workspace --workdir /mnt/workspace ocaz-finder bash

# in container:

export PATH=${PATH}:${HOME}/.local/bin
python3 -m pip install --editable .[dev]
uvicorn ocaz_finder.app:app --host 0.0.0.0 --port 8000 --reload
```
