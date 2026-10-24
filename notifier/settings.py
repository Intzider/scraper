import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")


def _list(name: str) -> list[str]:
    return [x.strip() for x in os.getenv(name, "").split(",") if x.strip()]


def _hours(value: str) -> range:
    start, _, end = value.partition("-")
    return range(int(start), int(end or start) + 1)


@dataclass(frozen=True)
class Settings:
    discord_token: str
    discord_channels: list[str]
    smtp_user: str
    smtp_password: str
    recipients: list[str]
    error_email: str
    state_file: Path
    timezone: ZoneInfo
    run_hours: range


def load() -> Settings:
    return Settings(
        discord_token=os.getenv("DISCORD_TOKEN", ""),
        discord_channels=_list("DISCORD_CHANNELS"),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_APP_PASSWORD", ""),
        recipients=_list("RECIPIENTS"),
        error_email=os.getenv("ERROR_EMAIL", ""),
        state_file=Path(os.getenv("STATE_FILE", ROOT / "state" / "seen.txt")),
        timezone=ZoneInfo(os.getenv("TIMEZONE", "Europe/Zagreb")),
        run_hours=_hours(os.getenv("RUN_HOURS", "7-21")),
    )
