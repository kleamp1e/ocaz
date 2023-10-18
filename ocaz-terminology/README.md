# ocaz-terminology

エロ画像、エロ動画を分類するための用語集です。

```sh
cd ~/repo/github.com/kleamp1e/ocaz/ocaz-terminology/
docker-compose build
docker-compose run --rm --service-ports editor-server bash
docker-compose exec editor-server pysen run format
```

for development:

```sh
python -m pip install --editable .[dev]
python -m pip freeze --exclude-editable > requirements.txt
pysen run format
pysen run lint
uvicorn --host=0.0.0.0 --port=8000 --app-dir=src --reload ocaz_terminology_editor_server.server:app
```
