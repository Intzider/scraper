# web_scraper

Checks [IsThereAnyDeal giveaways](https://isthereanydeal.com/giveaways/) and sends new free games by email and to Discord. Failures send the traceback to `ERROR_EMAIL`.

Sources are listed in `SOURCES` in `notifier/__main__.py`; each one is a function returning the URLs it currently lists. Sending, the seen-file and the hourly loop are shared.

## Notifier

```sh
cp .env.example .env   # fill in
python -m notifier             # one check
python -m notifier --loop      # check every hour in RUN_HOURS (what the container runs)
python -m notifier --dry-run   # fetch and print, nothing sent or saved
```

Already seen URLs are stored in `STATE_FILE`. An old `scraped/*_isthereanydeal.txt` file can be renamed to it as-is.

### Docker compose

```yaml
scraper:
  build:
    context: ./scraper
  image: a-scraper:latest
  container_name: scraper
  restart: unless-stopped
  init: true
  volumes:
    - ./data/scraper:/app/scraped        # seen.txt lives here
    - ./scraper/.env:/app/.env:ro
```

## Dependencies

Direct dependencies go in `requirements.in`; `requirements.txt` is generated with hashes:

```sh
pip install pip-tools
pip-compile --generate-hashes --strip-extras requirements.in            # after editing requirements.in
pip-compile --generate-hashes --strip-extras --upgrade requirements.in  # upgrade everything
```

Dependabot opens a weekly PR that does the upgrade for you (plus the Docker base image). CI builds the image and does a `--dry-run` against the live ITAD page, so a green PR is safe to merge.

