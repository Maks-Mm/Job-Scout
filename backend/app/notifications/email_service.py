#backend/app/notifications/email_service.py

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
            💰 Gehalt:
            {salary_min or ''} - {salary_max or ''} EUR
            </p>
            """


        cards += f"""

        <div style="
            border:1px solid #ddd;
            border-radius:12px;
            padding:20px;
            margin-bottom:15px;
            background:#ffffff;
            font-family:Arial;
        ">

            <h2 style="margin-top:0;color:#1d4ed8;">
                {title}
            </h2>


            <p>
                🏢 <b>Firma:</b> {company}
            </p>


            <p>
                📍 <b>Ort:</b> {city}
            </p>


            <p>
                🌐 <b>Quelle:</b> {source}
            </p>


            <p>
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
            ">
            Zum Job
            </a>

        </div>

        """



    html = f"""

    <html>

    <body style="
    background:#f3f4f6;
    padding:20px;
    ">


    <h1 style="
    font-family:Arial;
    ">
    Neue Jobangebote gefunden
    </h1>


    <p style="font-family:Arial;">
    Job Scout hat neue passende Stellen gefunden:
    </p>


    {cards}


    <p style="
    font-family:Arial;
    color:#666;
    ">
    Automatische Nachricht von Job Scout
    </p>


    </body>

    </html>

    """



    msg = MIMEMultipart("alternative")

    msg["Subject"] = "Neue Job Scout Ergebnisse"
    msg["From"] = EMAIL
    msg["To"] = receiver


    msg.attach(
        MIMEText(html, "html")
    )


    server = smtplib.SMTP(
        SMTP_SERVER,
        SMTP_PORT
    )


    server.starttls()


    server.login(
        EMAIL,
        PASSWORD
    )


    server.send_message(msg)

    server.quit()