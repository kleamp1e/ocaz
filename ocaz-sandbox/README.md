# ocaz-sandbox

```sh
cd ~/repo/github.com/kleamp1e/ocaz/ocaz-sandbox/
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --editable .
python3 -m pip install --editable .[dev]

pysen run lint
pysen run format

python3 -m ocaz_sandbox.scan_nginx --help
python3 -m ocaz_sandbox.scan_nginx http://localhost:8000/ > url.txt
python3 -m ocaz_sandbox.make_index --help
python3 -m ocaz_sandbox.add_url --help
cat url.txt | python3 -m ocaz_sandbox.add_url --stdin
python3 -m ocaz_sandbox.resolve_object_meta --help
```

```sh
cd ~/repo/github.com/kleamp1e/ocaz/sandbox/
docker-compose build
docker-compose up -d
open http://localhost:27002/

docker-compose run --rm sandbox
docker-compose run --rm --user $(id -u):$(id -g) --env HOME=/tmp/home sandbox
# export PATH=${PATH}:${HOME}/.local/bin
```
