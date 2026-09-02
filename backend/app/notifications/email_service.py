# backend/app/notifications/email_service.py

import smtplib
import os
from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def normalize_gmail_password(value: str | None) -> str:
    if not value:
        return ""
    return "".join(value.split()).strip()


EMAIL = os.environ.get("GMAIL_FROM") or "maxfilawwwrest@gmail.com"
PASSWORD = normalize_gmail_password(os.environ.get("GMAIL_APP_PASSWORD"))
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

print(
    "[EmailService] Configuration:"
    f" sender={EMAIL}"
    f" smtp={SMTP_SERVER}:{SMTP_PORT}"
    f" password_configured={bool(PASSWORD)}"
    f" frontend={FRONTEND_URL}"
    f" backend={BACKEND_URL}"
)

# How many hours ago a job is considered "fresh"
FRESH_HOURS = 24


def _is_fresh(date_str: str | None) -> bool:
    """Return True if the job was posted within the last FRESH_HOURS hours."""
    if not date_str:
        return False
    try:
        job_date = datetime.fromisoformat(date_str[:19])
        delta = datetime.utcnow() - job_date
        return delta.total_seconds() < FRESH_HOURS * 3600
    except Exception:
        return False


def _format_salary(salary_min, salary_max) -> str | None:
    if salary_min and salary_max:
        return f"€{int(salary_min):,} – €{int(salary_max):,} / Monat".replace(",", ".")
    if salary_max:
        return f"bis €{int(salary_max):,} / Monat".replace(",", ".")
    if salary_min:
        return f"ab €{int(salary_min):,} / Monat".replace(",", ".")
    return None


def _employment_label(emp_type: str | None) -> str:
    labels = {
        "parttime": "Teilzeit",
        "fulltime": "Vollzeit",
        "mini": "Minijob",
        "all": "",
    }
    return labels.get(emp_type or "", emp_type or "")


def _build_job_card(job: dict) -> str:
    title = job.get("title", "Unbekannter Job")
    company = job.get("company", "")
    city = job.get("city", "")
    source = job.get("source", "")
    date_str = job.get("date") or job.get("created_at") or job.get("posted_at") or ""
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")
    employment_type = job.get("employment_type", "")
    url = job.get("url", "#")

    fresh_badge = ""
    if _is_fresh(date_str):
        fresh_badge = """
        <span style="
            display:inline-block;
            background:#dcfce7;
            color:#166534;
            font-size:11px;
            font-weight:700;
            padding:2px 8px;
            border-radius:20px;
            margin-left:8px;
            vertical-align:middle;
            letter-spacing:0.3px;
        ">NEU</span>"""

    salary_html = ""
    salary_text = _format_salary(salary_min, salary_max)
    if salary_text:
        salary_html = f"""
        <p style="margin:6px 0;font-size:14px;color:#374151;">
            💰 <strong>Gehalt:</strong> {salary_text}
        </p>"""

    employment_html = ""
    emp_label = _employment_label(employment_type)
    if emp_label:
        employment_html = f"""
        <p style="margin:6px 0;font-size:14px;color:#374151;">
            ⏱️ <strong>Beschäftigung:</strong> {emp_label}
        </p>"""

    date_display = ""
    if date_str:
        try:
            d = datetime.fromisoformat(date_str[:10])
            date_display = d.strftime("%d.%m.%Y")
        except Exception:
            date_display = date_str[:10]

    date_html = ""
    if date_display:
        date_html = f"""
        <p style="margin:6px 0;font-size:13px;color:#6b7280;">
            📅 Veröffentlicht: {date_display}
        </p>"""

    company_html = f"""
        <p style="margin:6px 0;font-size:14px;color:#374151;">
            🏢 <strong>{company}</strong>
        </p>""" if company else ""

    source_badge = ""
    if source:
        source_badge = f"""
        <span style="
            display:inline-block;
            background:#f1f5f9;
            color:#475569;
            font-size:11px;
            padding:2px 8px;
            border-radius:10px;
            margin-top:10px;
        ">{source}</span>"""

    return f"""
    <div style="
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:20px 24px;
        margin-bottom:14px;
        background:#ffffff;
        border-left:4px solid #2563eb;
    ">
        <h2 style="margin:0 0 4px;color:#1d4ed8;font-size:17px;line-height:1.3;">
            {title}{fresh_badge}
        </h2>
        {company_html}
        <p style="margin:6px 0;font-size:14px;color:#374151;">
            📍 {city}
        </p>
        {employment_html}
        {salary_html}
        {date_html}
        {source_badge}
        <div style="margin-top:14px;">
            <a href="{url}" style="
                display:inline-block;
                padding:9px 18px;
                background:#2563eb;
                color:#ffffff;
                text-decoration:none;
                border-radius:8px;
                font-size:14px;
                font-weight:600;
            ">Zum Job →</a>
        </div>
    </div>"""


def _build_filter_summary(user_filters: dict) -> str:
    """Render a small 'Your active filters' block at the top of the email."""
    parts = []

    city = user_filters.get("city") or ""
    country = user_filters.get("country") or "Germany"
    emp = _employment_label(user_filters.get("employment_type"))
    min_s = user_filters.get("min_salary")
    max_s = user_filters.get("max_salary")
    keywords = user_filters.get("keywords") or ""

    if city:
        parts.append(f"📍 {city}, {country}")
    if emp:
        parts.append(f"⏱️ {emp}")
    salary_text = _format_salary(min_s, max_s)
    if salary_text:
        parts.append(f"💰 {salary_text}")
    if keywords:
        parts.append(f"🔍 {keywords}")

    if not parts:
        return ""

    rows = "".join(
        f'<span style="display:inline-block;margin:4px 6px 4px 0;background:#eff6ff;'
        f'color:#1d4ed8;padding:4px 10px;border-radius:20px;font-size:13px;">{p}</span>'
        for p in parts
    )

    return f"""
    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;margin-bottom:22px;">
        <p style="margin:0 0 8px;font-size:13px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">
            Deine aktiven Filter
        </p>
        <div>{rows}</div>
    </div>"""


def send_job_email(
    receiver: str,
    jobs: list[dict],
    unsubscribe_token: str | None = None,
    user_filters: dict | None = None,
) -> bool:
    """
    Send a structured, filtered job digest email.

    - Jobs are shown newest-first (caller should pre-sort).
    - Fresh jobs (< 24h) get a green NEU badge.
    - Active filter criteria are summarised at the top.
    - Max 20 jobs per email.
    """
    print(f"[EmailService] Preparing email for {receiver} with {len(jobs)} jobs")

    jobs_to_send = jobs[:20]
    filter_summary = _build_filter_summary(user_filters or {})
    cards_html = "".join(_build_job_card(job) for job in jobs_to_send)

    fresh_count = sum(1 for j in jobs_to_send if _is_fresh(
        j.get("date") or j.get("created_at") or j.get("posted_at") or ""
    ))

    subject_suffix = f" · {fresh_count} neu" if fresh_count else ""
    subject = f"Job Scout: {len(jobs_to_send)} passende Stellen{subject_suffix}"

    unsubscribe_section = ""
    if unsubscribe_token:
        link = f"{BACKEND_URL}/api/users/unsubscribe?token={unsubscribe_token}"
        unsubscribe_section = f"""
        <p style="font-size:12px;color:#94a3b8;margin-top:12px;">
            Keine Benachrichtigungen mehr? <a href="{link}" style="color:#2563eb;text-decoration:none;">Abmelden</a>
        </p>"""

    html = f"""
    <html>
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
    <body style="background:#f3f4f6;padding:24px;font-family:Arial,sans-serif;margin:0;">
        <div style="max-width:620px;margin:0 auto;">

            <div style="margin-bottom:22px;">
                <h1 style="color:#1e293b;font-size:22px;margin:0 0 4px;">🎯 Job Scout</h1>
                <p style="color:#64748b;font-size:14px;margin:0;">
                    {len(jobs_to_send)} passende Stellen gefunden
                    {f'· davon <strong style="color:#166534">{fresh_count} neu</strong>' if fresh_count else ''}
                </p>
            </div>

            {filter_summary}

            <div>
                {cards_html}
            </div>

            <div style="border-top:1px solid #e2e8f0;padding-top:18px;margin-top:24px;">
                <p style="font-size:12px;color:#94a3b8;margin:0;">
                    Automatische Nachricht von Job Scout · Du erhältst diese E-Mail, weil du Benachrichtigungen aktiviert hast.
                </p>
                {unsubscribe_section}
            </div>

        </div>
    </body>
    </html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = receiver
    msg.attach(MIMEText(html, "html"))

    try:
        if not EMAIL or not PASSWORD:
            print("[EmailService] ❌ Gmail credentials missing: check GMAIL_FROM and GMAIL_APP_PASSWORD")
            return False

        print("[EmailService] Connecting to SMTP…")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[EmailService] ✅ Email sent to {receiver}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EmailService] ❌ Auth error: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"[EmailService] ❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"[EmailService] ❌ Unexpected error: {e}")
        return False


def send_verification_email(receiver: str, token: str) -> bool:
    """Send email address verification link."""
    verify_link = f"{FRONTEND_URL}/verify-email?token={token}"

    html = f"""
    <html>
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
    <body style="background:#f3f4f6;padding:24px;font-family:Arial,sans-serif;margin:0;">
        <div style="max-width:560px;margin:0 auto;background:#ffffff;padding:32px;border-radius:16px;border:1px solid #e5e7eb;">
            <h1 style="color:#1d4ed8;font-size:22px;margin:0 0 12px;">E-Mail bestätigen</h1>
            <p style="color:#374151;font-size:15px;line-height:1.6;margin:0 0 20px;">
                Vielen Dank! Klicke auf den Button, um deine E-Mail-Adresse für Job Scout Benachrichtigungen zu bestätigen.
            </p>
            <a href="{verify_link}" style="
                display:inline-block;
                padding:12px 24px;
                background:#2563eb;
                color:#ffffff;
                text-decoration:none;
                border-radius:10px;
                font-size:15px;
                font-weight:600;
            ">E-Mail bestätigen →</a>
            <p style="color:#94a3b8;font-size:12px;margin-top:24px;">
                Wenn du das nicht angefordert hast, kannst du diese E-Mail ignorieren.
            </p>
        </div>
    </body>
    </html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Job Scout · E-Mail-Adresse bestätigen"
    msg["From"] = EMAIL
    msg["To"] = receiver
    msg.attach(MIMEText(html, "html"))

    try:
        if not EMAIL or not PASSWORD:
            print(
                "[EmailService] Verification email failed: "
                "missing Gmail credentials"
            )
            return False

        print(
            f"[EmailService] Connecting to Gmail SMTP for verification → {receiver}"
        )

        server = smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT,
            timeout=30,
        )

        server.starttls()
        print("[EmailService] SMTP TLS established")

        server.login(
            EMAIL,
            PASSWORD,
        )
        print("[EmailService] SMTP authentication successful")

        response = server.send_message(msg)
        print(f"[EmailService] SMTP send response: {response}")

        server.quit()
        print(
            f"[EmailService] Verification email accepted for delivery to {receiver}"
        )

        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[EmailService] Gmail authentication failed: {e}")
        return False

    except smtplib.SMTPException as e:
        print(f"[EmailService] SMTP error: {e}")
        return False

    except Exception as e:
        print(f"[EmailService] Unexpected verification error: {repr(e)}")
        return False