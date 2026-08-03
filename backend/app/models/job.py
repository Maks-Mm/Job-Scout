#backend/app/models/job.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String)
    city = Column(String)
    salary_min = Column(Float)
    salary_max = Column(Float)
    currency = Column(String, default="EUR")
    url = Column(String, unique=True, nullable=False)
    source = Column(String)
    date = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user_jobs = relationship("UserJob", back_populates="job")