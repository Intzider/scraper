import argparse
import time
import traceback
from datetime import datetime, timedelta

from . import settings as settings_module
from .itad import fetch_giveaways
from .notify import send_discord, send_email
from .state import load_seen, mark_seen


def run(settings: settings_module.Settings, dry_run: bool = False) -> None:
    seen = load_seen(settings.state_file)
    new = [url for url in dict.fromkeys(fetch_giveaways()) if url not in seen]
    if not new:
        print("isthereanydeal --> no new hits", flush=True)
        return

    print(f"isthereanydeal --> {len(new)} new hits", flush=True)
    # <> stops discord from expanding every link into an embed
    body = "\n".join(f"<{url}>" for url in new)
    if dry_run:
        print(body)
        return

    now = datetime.now(settings.timezone).strftime("%m/%d/%Y, %H:%M")
    if settings.recipients:
        send_email(settings, f"isthereanydeal -- {now}", body, settings.recipients)
    if settings.discord_channels:
        send_discord(settings, body)
    mark_seen(settings.state_file, new)


def run_safely(settings: settings_module.Settings) -> bool:
    try:
        run(settings)
        return True
    except Exception:
        error = traceback.format_exc()
        print(error, flush=True)
        if settings.error_email:
            try:
                send_email(settings, "Scraper failed", error, [settings.error_email])
            except Exception:
                traceback.print_exc()
        return False


def loop(settings: settings_module.Settings) -> None:
    """Run at the top of every hour in RUN_HOURS, like the old systemd timer."""
    while True:
        now = datetime.now(settings.timezone)
        if now.hour in settings.run_hours:
            run_safely(settings)
        next_hour = (datetime.now(settings.timezone) + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        time.sleep(max((next_hour - datetime.now(settings.timezone)).total_seconds(), 1))


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m notifier")
    parser.add_argument("--loop", action="store_true", help="keep running and check every hour in RUN_HOURS")
    parser.add_argument("--dry-run", action="store_true", help="fetch and print new hits without sending or saving")
    args = parser.parse_args()

    settings = settings_module.load()
    if args.dry_run:
        run(settings, dry_run=True)
    elif args.loop:
        loop(settings)
    elif not run_safely(settings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
