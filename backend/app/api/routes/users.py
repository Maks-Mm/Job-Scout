#backend/app/api/routes/users.py

import os
import uuid
from datetime import datetime, timedelta
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

    timestamps = [
        timestamp
        for timestamp in rate_limit_store.get(client_ip, [])
        if timestamp > window_start
    ]

    timestamps.append(now)
    rate_limit_store[client_ip] = timestamps

    if len(timestamps) > RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Zu viele Anfragen. Bitte versuchen Sie es in einer Minute erneut.",
        )

class AlertPreferences(BaseModel):
    email: EmailStr
    alerts_enabled: bool = False
    keywords: str | None = None
    city: str | None = None
    country: str | None = "Germany"
    interval: str = "6h"
    consent: bool = False
    language: str = "de"
    employment_type: str | None = "all"
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

def refresh_alert_state(user: User):
    """
    Single source of truth for whether the notifier may send alerts.

    A permanent alert is active only when:
    1. Email is verified.
    2. User consent exists.
    3. Alerts have not been explicitly disabled.
    """
    user.alerts_enabled = bool(
        user.verified_email and user.consent_given and user.alerts_enabled
    )

def _apply_preferences(user: User, preferences: AlertPreferences):
    user.keywords = preferences.keywords or ""
    user.city = preferences.city or ""
    user.country = preferences.country or "Germany"
    user.alert_interval = preferences.interval or "6h"
    user.language = preferences.language or "de"
    user.employment_type = preferences.employment_type or "all"
    user.job_category = preferences.job_category or "all"
    user.min_salary = preferences.min_salary
    user.max_salary = preferences.max_salary

    # Consent is independent from verification.
    user.consent_given = bool(preferences.consent)
    user.consent_date = (
        datetime.utcnow() if preferences.consent else None
    )

    # Keep the user's requested subscription state separately in this flow.
    # Unverified users cannot become actually active yet.
    if not preferences.consent or not preferences.alerts_enabled:
        user.alerts_enabled = False
    elif user.verified_email:
        user.alerts_enabled = True
    else:
        user.alerts_enabled = False

def should_send_verification(
    user: User,
    now: datetime | None = None,
) -> bool:
    if user.verified_email:
        return False

    current_time = now or datetime.utcnow()

    token_missing = not user.email_verification_token

    token_expired = (
        user.email_verification_expires_at is None
        or user.email_verification_expires_at <= current_time
    )

    return token_missing or token_expired

@router.post("/api/users/alerts")
def save_alert_preferences(
    request: Request,
    preferences: AlertPreferences,
):
    check_rate_limit(request)

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == preferences.email)
            .first()
        )

        if not user:
            base_username = preferences.email.split("@")[0]

            existing = (
                db.query(User)
                .filter(User.username == base_username)
                .first()
            )

            username = (
                base_username
                if not existing
                else f"{base_username}_{uuid.uuid4().hex[:8]}"
            )

            user = User(
                email=preferences.email,
                username=username,
                alerts_enabled=False,
                consent_given=False,
                verified_email=False,
                unsubscribe_token=uuid.uuid4().hex,
            )

            db.add(user)
            db.flush()

        if not user.unsubscribe_token:
            user.unsubscribe_token = uuid.uuid4().hex

        _apply_preferences(user, preferences)

        verification_sent = False

        # A verification email is needed only when:
        # - user consented
        # - email is still unverified
        # - no valid token already exists
        if preferences.consent and not user.verified_email:
            now = datetime.utcnow()

            if should_send_verification(user, now):
                token = str(uuid.uuid4())

                user.email_verification_token = token
                user.email_verification_expires_at = (
                    now + timedelta(hours=24)
                )

                # Persist the token before sending.
                db.commit()

                sent = send_verification_email(
                    user.email,
                    token,
                )

                if not sent:
                    user.email_verification_token = None
                    user.email_verification_expires_at = None
                    db.commit()

                    raise HTTPException(
                        status_code=500,
                        detail=(
                            "Verification email could not be sent. "
                            "Please try again later."
                        ),
                    )

                verification_sent = True

        db.commit()

        return {
            "success": True,
            "verification_sent": verification_sent,
            "verified_email": bool(user.verified_email),
            "alerts_enabled": bool(user.alerts_enabled),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        db.close()

@router.patch("/api/users/alerts")
def update_alert_preferences(
    request: Request,
    update: AlertUpdate,
):
    check_rate_limit(request)

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == update.email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        # Filter updates
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

        # Explicit alert state change
        if update.alerts_enabled is not None:
            if update.alerts_enabled:
                user.alerts_enabled = bool(
                    user.verified_email and user.consent_given
                )
            else:
                user.alerts_enabled = False

        # Consent change
        if update.consent is not None:
            user.consent_given = bool(update.consent)

            user.consent_date = (
                datetime.utcnow()
                if update.consent
                else None
            )

            if not update.consent:
                user.alerts_enabled = False

            elif not user.verified_email:
                now = datetime.utcnow()

                if should_send_verification(user, now):
                    token = str(uuid.uuid4())

                    user.email_verification_token = token
                    user.email_verification_expires_at = (
                        now + timedelta(hours=24)
                    )

                    db.commit()

                    sent = send_verification_email(
                        user.email,
                        token,
                    )

                    if not sent:
                        user.email_verification_token = None
                        user.email_verification_expires_at = None
                        db.commit()

                        raise HTTPException(
                            status_code=500,
                            detail="Verification email could not be sent.",
                        )

        # Never leave an unverified or non-consenting user active.
        if not user.verified_email or not user.consent_given:
            user.alerts_enabled = False

        db.commit()

        return {
            "success": True,
            "verified_email": bool(user.verified_email),
            "alerts_enabled": bool(user.alerts_enabled),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        db.close()

@router.get("/api/users/verify-email")
def verify_email(token: str):
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Missing verification token.",
        )

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email_verification_token == token)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Invalid verification token.",
            )

        now = datetime.utcnow()

        # Reject expired tokens before changing the account state.
        if (
            user.email_verification_expires_at is None
            or user.email_verification_expires_at <= now
        ):
            user.email_verification_token = None
            user.email_verification_expires_at = None
            user.alerts_enabled = False

            db.commit()

            raise HTTPException(
                status_code=410,
                detail=(
                    "Der Verifizierungslink ist abgelaufen. "
                    "Bitte fordere eine neue Bestätigungs-E-Mail an."
                ),
            )

        # Verification confirms email ownership only.
        user.verified_email = True

        # Consume the token.
        user.email_verification_token = None
        user.email_verification_expires_at = None

        # IMPORTANT:
        # Do not force consent here.
        # Consent was already recorded when the user explicitly checked
        # the subscription checkbox.
        #
        # This replaces:
        # user.consent_given = bool(user.consent_given or True)

        # Activate permanent alerts only when prior consent exists.
        user.alerts_enabled = bool(user.consent_given)

        db.commit()

        return {
            "success": True,
            "message": "E-Mail-Adresse erfolgreich bestätigt.",
            "verified_email": True,
            "alerts_enabled": bool(user.alerts_enabled),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        db.close()

@router.get("/api/users/unsubscribe")
def unsubscribe(token: str):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.unsubscribe_token == token)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Invalid unsubscribe token.",
            )

        user.alerts_enabled = False
        user.consent_given = False
        user.consent_date = None

        db.commit()

        return {
            "success": True,
            "message": "E-Mail-Benachrichtigungen wurden deaktiviert.",
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        db.close()

@router.delete("/api/users/alerts")
def disable_alerts(
    request: Request,
    disable: AlertDelete,
):
    check_rate_limit(request)

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == disable.email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        user.alerts_enabled = False
        user.consent_given = False
        user.consent_date = None

        db.commit()

        return {
            "success": True,
            "message": "E-Mail-Benachrichtigungen wurden deaktiviert.",
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        db.close()

# DEV/TEST ONLY
@router.post("/api/users/force-verify")
def force_verify(email: str):
    if os.getenv("ALLOW_DEV_EMAIL_DEBUG", "").lower() not in {
        "1",
        "true",
        "yes",
    }:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is disabled in production.",
        )

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {email} not found.",
            )

        user.verified_email = True
        user.email_verification_token = None
        user.email_verification_expires_at = None

        # Respect existing consent.
        user.alerts_enabled = bool(user.consent_given)

        db.commit()

        return {
            "success": True,
            "message": f"{email} is now verified.",
            "alerts_enabled": bool(user.alerts_enabled),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        db.close()

# DEV/TEST ONLY
@router.get("/api/users/status")
def user_status(email: str):
    if os.getenv("ALLOW_DEV_EMAIL_DEBUG", "").lower() not in {
        "1",
        "true",
        "yes",
    }:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is disabled in production.",
        )

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {email} not found.",
            )

        return {
            "email": user.email,
            "alerts_enabled": bool(user.alerts_enabled),
            "consent_given": bool(user.consent_given),
            "verified_email": bool(user.verified_email),
            "email_verification_token": user.email_verification_token,
            "email_verification_expires_at": user.email_verification_expires_at,
            "unsubscribe_token": user.unsubscribe_token,
            "alert_interval": user.alert_interval,
            "country": user.country,
            "city": user.city,
            "employment_type": user.employment_type,
            "job_category": user.job_category,
            "min_salary": user.min_salary,
            "max_salary": user.max_salary,
            "keywords": user.keywords,
            "notifier_eligible": bool(
                user.alerts_enabled
                and user.consent_given
                and user.verified_email
            ),
        }

    except HTTPException:
        raise

    finally:
        db.close()