# backend/app/api/routes/users.py

from datetime import datetime
import uuid
from time import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr

from app.core.database import SessionLocal
from app.models.user import User
from app.notifications.email_service import send_verification_email

router = APIRouter()

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 5
rate_limit_store: dict[str, list[float]] = {}


def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    timestamps = [t for t in rate_limit_store.get(client_ip, []) if t > window_start]
    timestamps.append(now)
    rate_limit_store[client_ip] = timestamps
    if len(timestamps) > RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Zu viele Anfragen. Bitte versuchen Sie es in einer Minute erneut.",
        )


class AlertPreferences(BaseModel):
    email: EmailStr
    alerts_enabled: bool = True
    keywords: str | None = None
    city: str | None = None
    country: str | None = "Germany"
    interval: str = "6h"
    consent: bool = False
    # ── New filter fields ────────────────────────────────────────────────────
    language: str = "de"
    employment_type: str | None = "all"   # "parttime" | "fulltime" | "mini" | "all"
    job_category: str | None = "all"
    min_salary: int | None = None
    max_salary: int | None = None


class AlertUpdate(BaseModel):
    email: EmailStr
    alerts_enabled: bool | None = None
    keywords: str | None = None
    city: str | None = None
    country: str | None = None
    interval: str | None = None
    consent: bool | None = None
    language: str | None = None
    employment_type: str | None = None
    job_category: str | None = None
    min_salary: int | None = None
    max_salary: int | None = None


class AlertDelete(BaseModel):
    email: EmailStr


def _apply_preferences(user: User, preferences: AlertPreferences):
    """Write all alert preference fields onto a User ORM object."""
    user.alerts_enabled = preferences.alerts_enabled
    user.keywords = preferences.keywords or ""
    user.city = preferences.city or ""
    user.country = preferences.country or "Germany"
    user.alert_interval = preferences.interval
    user.consent_given = preferences.consent
    user.consent_date = datetime.utcnow() if preferences.consent else None
    # Filter fields
    user.language = preferences.language or "de"
    user.employment_type = preferences.employment_type or "all"
    user.job_category = preferences.job_category or "all"
    user.min_salary = preferences.min_salary
    user.max_salary = preferences.max_salary


@router.post("/api/users/alerts")
def save_alert_preferences(request: Request, preferences: AlertPreferences):
    """Save or update a user's alert preferences and send a verification email."""
    check_rate_limit(request)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == preferences.email).first()

        if not user:
            base_username = preferences.email.split("@")[0]
            existing = db.query(User).filter(User.username == base_username).first()
            username = base_username if not existing else f"{base_username}_{uuid.uuid4().hex[:8]}"
            user = User(
                email=preferences.email,
                username=username,
                unsubscribe_token=uuid.uuid4().hex,
            )
            db.add(user)
            db.flush()

        if not user.unsubscribe_token:
            user.unsubscribe_token = uuid.uuid4().hex

        _apply_preferences(user, preferences)

        verification_sent = False
        if preferences.consent and not user.verified_email:
            if not user.email_verification_token:
                user.email_verification_token = str(uuid.uuid4())
                db.commit()
                sent = send_verification_email(preferences.email, user.email_verification_token)
                if not sent:
                    user.email_verification_token = None
                    db.commit()
                    raise HTTPException(
                        status_code=500,
                        detail="Verification email could not be sent. Please try again later.",
                    )
                verification_sent = True

        db.commit()
        return {"success": True, "verification_sent": verification_sent}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.patch("/api/users/alerts")
def update_alert_preferences(request: Request, update: AlertUpdate):
    """Partially update an existing user's alert preferences."""
    check_rate_limit(request)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == update.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        if update.alerts_enabled is not None:
            user.alerts_enabled = update.alerts_enabled
            if not update.alerts_enabled:
                user.consent_given = False
                user.consent_date = None

        if update.keywords is not None:
            user.keywords = update.keywords
        if update.city is not None:
            user.city = update.city
        if update.country is not None:
            user.country = update.country
        if update.interval is not None:
            user.alert_interval = update.interval
        if update.language is not None:
            user.language = update.language
        if update.employment_type is not None:
            user.employment_type = update.employment_type
        if update.job_category is not None:
            user.job_category = update.job_category
        if update.min_salary is not None:
            user.min_salary = update.min_salary
        if update.max_salary is not None:
            user.max_salary = update.max_salary

        if update.consent is not None:
            user.consent_given = update.consent
            user.consent_date = datetime.utcnow() if update.consent else None
            if update.consent and not user.verified_email:
                if not user.email_verification_token:
                    user.email_verification_token = str(uuid.uuid4())
                    db.commit()
                    sent = send_verification_email(user.email, user.email_verification_token)
                    if not sent:
                        user.email_verification_token = None
                        db.commit()
                        raise HTTPException(
                            status_code=500,
                            detail="Verification email could not be sent. Please try again later.",
                        )

        db.commit()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/api/users/unsubscribe")
def unsubscribe(token: str):
    """Disable alerts via unsubscribe token."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.unsubscribe_token == token).first()
        if not user:
            raise HTTPException(status_code=404, detail="Invalid unsubscribe token.")
        user.alerts_enabled = False
        user.consent_given = False
        user.consent_date = None
        db.commit()
        return {"success": True, "message": "E-Mail-Benachrichtigungen wurden deaktiviert."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/api/users/alerts")
def disable_alerts(request: Request, disable: AlertDelete):
    """Disable alert notifications for an existing user."""
    check_rate_limit(request)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == disable.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        user.alerts_enabled = False
        user.consent_given = False
        user.consent_date = None
        db.commit()
        return {"success": True, "message": "E-Mail-Benachrichtigungen wurden deaktiviert."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/api/users/verify-email")
def verify_email(token: str):
    """Verify a user's email address via token."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email_verification_token == token).first()
        if not user:
            raise HTTPException(status_code=404, detail="Invalid verification token.")
        user.verified_email = True
        user.email_verification_token = None
        db.commit()
        return {"success": True, "message": "E-Mail-Adresse erfolgreich bestätigt."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()