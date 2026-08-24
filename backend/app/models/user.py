#backend/app/models/user.py

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=True)

    # Alert state
    # A user receives alerts only when all three are True:
    # verified_email AND consent_given AND alerts_enabled.
    alerts_enabled = Column(Boolean, default=False, nullable=False)
    alert_interval = Column(String, default="6h", nullable=False)

    # Consent
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime, nullable=True)

    # Email verification
    verified_email = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String, nullable=True, index=True)
    email_verification_expires_at = Column(DateTime, nullable=True)

    # Unsubscribe
    unsubscribe_token = Column(String, nullable=True, unique=True, index=True)

    # Filter preferences
    country = Column(String, default="Germany")
    city = Column(String, nullable=True)
    keywords = Column(String, nullable=True)
    language = Column(String, default="de")
    employment_type = Column(String, default="all")
    job_category = Column(String, default="all")
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)

    # Relationships
    user_jobs = relationship("UserJob", back_populates="user")