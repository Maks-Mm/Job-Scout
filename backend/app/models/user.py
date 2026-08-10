# backend/app/models/user.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Keep this unique
    username = Column(String, nullable=True)  # Remove unique=True or make nullable
    alerts_enabled = Column(Boolean, default=False)
    alert_interval = Column(String, default="6h")
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime, nullable=True)
    verified_email = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    unsubscribe_token = Column(String, unique=True, nullable=True)
    country = Column(String, default="Germany")
    city = Column(String, nullable=True)
    keywords = Column(String, nullable=True)
    
    user_jobs = relationship("UserJob", back_populates="user")