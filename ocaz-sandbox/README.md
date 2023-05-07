# ocaz-sandbox

```sh
cd ~/repo/github.com/kleamp1e/ocaz/ocaz-sandbox/
python -m venv .venv
source .venv/bin/activate
python -m pip install --editable .

pysen run lint
pysen run format

python -m ocaz_sandbox.scan_nginx
```
