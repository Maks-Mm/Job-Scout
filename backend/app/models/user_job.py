# backend/app/models/user_job.py
# This model MUST be imported before User and Job are used in queries.
# Import it in app/models/__init__.py to ensure SQLAlchemy registers it.

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserJob(Base):
    __tablename__ = "user_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    job_url = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="user_jobs")
    job = relationship("Job", back_populates="user_jobs")