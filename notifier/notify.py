import smtplib
import ssl
from email.message import EmailMessage

import requests

from .settings import Settings

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(settings: Settings, subject: str, body: str, recipients: list[str]) -> None:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=ssl.create_default_context())
        server.login(settings.smtp_user, settings.smtp_password)
        for recipient in recipients:
            message = EmailMessage()
            message["From"] = settings.smtp_user
            message["To"] = recipient
            message["Subject"] = subject
            message.set_content(body)
            server.send_message(message)


def send_discord(settings: Settings, content: str) -> None:
    headers = {"authorization": "Bot " + settings.discord_token}
    for channel in settings.discord_channels:
        response = requests.post(
            f"https://discord.com/api/channels/{channel}/messages",
            json={"content": content, "embeds": []},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
