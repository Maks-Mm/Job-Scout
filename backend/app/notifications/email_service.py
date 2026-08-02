#backend/app/notifications/email_service.py

import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Lade die .env Datei
load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL = "maxfilawwwrest@gmail.com"
PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")  # Holt Passwort aus .env


def send_job_email(receiver, jobs):
    body = "Neue Jobs gefunden:\n\n"

    for job in jobs[:20]:
        body += (
            f"{job['title']}\n"
            f"{job['company']}\n"
            f"{job['city']}\n"
            f"{job['url']}\n\n"
        )

    msg = MIMEText(body)
    msg["Subject"] = "Neue Job Scout Ergebnisse"
    msg["From"] = EMAIL
    msg["To"] = receiver

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()

    

    # Dieser Teil ist NUR für Tests - füge ihn ans Ende der Datei:
if __name__ == "__main__":
    send_job_email("maxfilawwwrest@gmail.com", [
        {"title": "Test Job", "company": "Test Co", "city": "Berlin", "url": "https://example.com"}
    ])