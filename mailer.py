import json
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

__all__ = ["send_email"]

SMTP_SERVER = "smtp.gmail.com"
PORT = 587


def get_email(directory: str):
    with open(os.path.join(directory, 'config', "sender_mail.json"), "r") as file:
        mail = json.load(file)
        return mail["email"], mail["app"], mail['error_email']


def create_message(sender_email: str, recipient: str, subject: str, payload: str):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(payload, "plain"))

    return message.as_string()


def send_email(directory: str, subject: str, payload: str, recipients: list[str]):
    (sender_email, sender_password, error_email) = get_email(directory)

    with smtplib.SMTP(SMTP_SERVER, PORT) as server:
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(sender_email, sender_password)
        for recipient in recipients:
            if "error" in subject or "exception" in payload:
                subject += recipient
                server.sendmail(sender_email, error_email, create_message(sender_email, error_email, subject, payload))
                return
            server.sendmail(sender_email, recipient, create_message(sender_email, recipient, subject, payload))
