# ocaz-simple-browser

```sh
cd ~/repo/github.com/kleamp1e/ocaz/sandbox/
docker-compose build ocaz-simple-browser
docker-compose up -d ocaz-simple-browser
docker-compose run --rm --service-ports ocaz-simple-browser
docker-compose run --rm --service-ports --volume ../ocaz-simple-browser:/mnt/workspace --workdir /mnt/workspace/app ocaz-simple-browser sh
docker-compose run --rm --service-ports --volume ../ocaz-simple-browser:/mnt/workspace --workdir /mnt/workspace/app ocaz-simple-browser npm run dev
```
