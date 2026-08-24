# backend/app/models/job.py

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    city = Column(String, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    currency = Column(String, default="EUR")
    url = Column(String, unique=True, nullable=False, index=True)
    source = Column(String, nullable=True)
    date = Column(String, nullable=True)

    # IMPORTANT: back_populates name must match UserJob.job
    user_jobs = relationship("UserJob", back_populates="job")