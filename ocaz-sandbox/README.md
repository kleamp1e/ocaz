# ocaz-sandbox

```sh
cd ~/repo/github.com/kleamp1e/ocaz/ocaz-sandbox/
python -m venv .venv
source .venv/bin/activate
python -m pip install --editable .
python -m pip install --editable .[dev]

pysen run lint
pysen run format

python -m ocaz_sandbox.scan_nginx --help
python -m ocaz_sandbox.scan_nginx http://localhost:8000/ > url.txt
```

```sh
cd ~/repo/github.com/kleamp1e/ocaz/sandbox/
docker-compose build
docker-compose up -d
open http://localhost:27002/

docker-compose run --rm sandbox
```
