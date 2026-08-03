#backend/app/models/user_job.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class UserJob(Base):
    __tablename__ = "user_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    job_url = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.now)

    # Relationships
    user = relationship("User", back_populates="user_jobs")
    job = relationship("Job", back_populates="user_jobs")