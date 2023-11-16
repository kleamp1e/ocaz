# ocaz-terminology

エロ画像、エロ動画を分類するための用語集です。

```sh
cd ~/repo/github.com/kleamp1e/ocaz/ocaz-terminology/editor-server
python -m venv env
source env/bin/activate
python -m pip install --editable ".[dev]"
python -m pip freeze --exclude-editable > requirements.txt
python -m pysen run format
python -m pysen run lint

export DATA_DIR=$(pwd)/../data
export FRAGMENT_DIR=${DATA_DIR}/term/fragment
python -m uvicorn --host=0.0.0.0 --port=8000 --app-dir=src --reload ocaz_terminology_editor_server.server:app
python -m ocaz_terminology_editor_server.pack --output-jsonl ${DATA_DIR}/term/latest.jsonl
python -m ocaz_terminology_editor_server.prepare_translate -c 15 | pbcopy
cat in.txt | python -m ocaz_terminology_editor_server.to_fragment
python -m ocaz_terminology_editor_server.stats

jq -r . ${DATA_DIR}/term/v0.0.1.jsonl > ${DATA_DIR}/term/v0.0.1.txt
jq -r . ${DATA_DIR}/term/latest.jsonl > ${DATA_DIR}/term/latest.txt
```

```sh
cd ~/repo/github.com/kleamp1e/ocaz/ocaz-terminology/editor-ui/src/
npm run dev
```

## タスク

* [x] 代表語の編集画面をダイアログ化する
* [x] 同義語の編集画面をダイアログ化する
* [x] タグをフィルタする機能を追加する
* [x] タグの一覧を色分けして表示する
* [x] フラグメントを結合したJSONLファイルを生成する
