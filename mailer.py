import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
PORT = 587

sender_email = "throwawaylmnjuskalo@gmail.com"
sender_password = "taropqiporprprvu"


def get_message(recipient: str, subject: str, payload: str):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(payload, "plain"))

    return message.as_string()


def send_email(subject: str, payload: str, recipients: list[str]):
    with smtplib.SMTP(SMTP_SERVER, PORT) as server:
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(sender_email, sender_password)
        for recipient in recipients:
            server.sendmail(sender_email, recipient, get_message(recipient, subject, payload))
