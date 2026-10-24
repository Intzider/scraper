import argparse
import logging
import time
import traceback
from collections.abc import Callable
from datetime import datetime, timedelta

from . import settings as settings_module
from .itad import fetch_giveaways
from .notify import send_discord, send_email
from .state import load_seen, mark_seen

log = logging.getLogger("notifier")


# name -> function returning the urls currently listed by that source
SOURCES: dict[str, Callable[[], list[str]]] = {
    "isthereanydeal": fetch_giveaways,
}


def run(settings: settings_module.Settings, dry_run: bool = False) -> None:
    for name, fetch in SOURCES.items():
        seen = load_seen(settings.state_file)
        new = [url for url in dict.fromkeys(fetch()) if url not in seen]
        if not new:
            log.info("%s --> no new hits", name)
            continue

        log.info("%s --> %d new hits", name, len(new))
        # <> stops discord from expanding every link into an embed
        body = "\n".join(f"<{url}>" for url in new)
        if dry_run:
            print(body)
            continue

        now = datetime.now(settings.timezone).strftime("%m/%d/%Y, %H:%M")
        if settings.recipients:
            send_email(settings, f"{name} -- {now}", body, settings.recipients)
        if settings.discord_channels:
            send_discord(settings, body)
        mark_seen(settings.state_file, new)


def run_safely(settings: settings_module.Settings) -> bool:
    try:
        run(settings)
        return True
    except Exception:
        error = traceback.format_exc()
        log.error("run failed\n%s", error)
        if settings.error_email:
            try:
                send_email(settings, "Scraper failed", error, [settings.error_email])
            except Exception:
                log.exception("sending error email failed")
        return False


def loop(settings: settings_module.Settings) -> None:
    """Run at the top of every hour in RUN_HOURS, like the old systemd timer."""
    while True:
        now = datetime.now(settings.timezone)
        if now.hour in settings.run_hours:
            run_safely(settings)
        next_hour = (datetime.now(settings.timezone) + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        time.sleep(max((next_hour - datetime.now(settings.timezone)).total_seconds(), 1))


def setup_logging(settings: settings_module.Settings) -> None:
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    # timestamps in TIMEZONE instead of the container's UTC
    formatter.converter = lambda ts: datetime.fromtimestamp(ts, settings.timezone).timetuple()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler])


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m notifier")
    parser.add_argument("--loop", action="store_true", help="keep running and check every hour in RUN_HOURS")
    parser.add_argument("--dry-run", action="store_true", help="fetch and print new hits without sending or saving")
    args = parser.parse_args()

    settings = settings_module.load()
    setup_logging(settings)
    if args.dry_run:
        run(settings, dry_run=True)
    elif args.loop:
        loop(settings)
    elif not run_safely(settings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
