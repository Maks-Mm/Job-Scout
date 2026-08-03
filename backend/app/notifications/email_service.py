# backend/app/notifications/email_service.py

import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


load_dotenv()


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL = "maxfilawwwrest@gmail.com"
PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")



def send_job_email(receiver, jobs):
    """
    Send HTML email with job cards to the receiver
    """
    print(f"[EmailService] Preparing mail for {receiver} with {len(jobs)} jobs")
    
    cards = ""

    for job in jobs[:20]:
        title = job.get("title", "Unbekannter Job")
        company = job.get("company", "Unbekannte Firma")
        city = job.get("city", "")
        source = job.get("source", "")
        date = job.get("date", "")
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        url = job.get("url", "#")

        salary = ""

        if salary_min or salary_max:
            salary = f"""
            <p>
                💰 <b>Gehalt:</b> {salary_min or ''} - {salary_max or ''} EUR
            </p>
            """

        cards += f"""
        <div style="
            border:1px solid #ddd;
            border-radius:12px;
            padding:20px;
            margin-bottom:15px;
            background:#ffffff;
            font-family:Arial, sans-serif;
        ">
            <h2 style="margin-top:0;color:#1d4ed8;font-size:20px;">
                {title}
            </h2>
            <p style="margin:5px 0;">
                🏢 <b>Firma:</b> {company}
            </p>
            <p style="margin:5px 0;">
                📍 <b>Ort:</b> {city}
            </p>
            <p style="margin:5px 0;">
                🌐 <b>Quelle:</b> {source}
            </p>
            <p style="margin:5px 0;">
                📅 <b>Datum:</b> {date}
            </p>
            {salary}
            <a href="{url}"
                style="
                    display:inline-block;
                    padding:10px 18px;
                    background:#2563eb;
                    color:white;
                    text-decoration:none;
                    border-radius:8px;
                    margin-top:10px;
                    font-weight:bold;
                ">
                Zum Job →
            </a>
        </div>
        """

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="
        background:#f3f4f6;
        padding:20px;
        font-family:Arial, sans-serif;
        margin:0;
    ">
        <div style="max-width:600px;margin:0 auto;">
            <h1 style="
                font-family:Arial, sans-serif;
                color:#1e293b;
                font-size:24px;
            ">
                🎯 Neue Jobangebote gefunden
            </h1>
            <p style="font-family:Arial, sans-serif;color:#475569;font-size:16px;">
                Job Scout hat neue passende Stellen für dich gefunden:
            </p>
            <div style="margin-top:20px;">
                {cards}
            </div>
            <p style="
                font-family:Arial, sans-serif;
                color:#94a3b8;
                font-size:12px;
                margin-top:30px;
                border-top:1px solid #e2e8f0;
                padding-top:20px;
            ">
                Automatische Nachricht von Job Scout • Du erhältst diese E-Mail, weil du Benachrichtigungen aktiviert hast.
            </p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Neue Job Scout Ergebnisse ({len(jobs)} Stellen)"
    msg["From"] = EMAIL
    msg["To"] = receiver

    msg.attach(MIMEText(html, "html"))

    # Send email with error handling
    try:
        print("[EmailService] Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        print("[EmailService] Starting TLS...")
        server.starttls()
        
        print("[EmailService] Logging in...")
        server.login(EMAIL, PASSWORD)
        
        print(f"[EmailService] Sending email to {receiver}...")
        server.send_message(msg)
        
        print("[EmailService] ✅ Email sent successfully!")
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EmailService] ❌ SMTP Authentication Error: {e}")
        print("[EmailService] Please check your GMAIL_APP_PASSWORD environment variable")
        return False
        
    except smtplib.SMTPException as e:
        print(f"[EmailService] ❌ SMTP Error: {e}")
        return False
        
    except Exception as e:
        print(f"[EmailService] ❌ Unexpected error: {e}")
        return False