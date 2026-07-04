#backend/app/models/job.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime
)

from sqlalchemy.sql import func

from app.core.database import Base


class Job(Base):

    __tablename__ = "jobs"


    id = Column(
        Integer,
        primary_key=True
    )


    title = Column(
        String(255),
        nullable=False
    )


    company = Column(
        String(255)
    )


    city = Column(
        String(100)
    )


    country = Column(
        String(100),
        default="Germany"
    )


    salary_min = Column(
        Float
    )


    salary_max = Column(
        Float
    )


    currency = Column(
        String(10),
        default="EUR"
    )


    category = Column(
        String(100)
    )


    description = Column(
        Text
    )


    url = Column(
        String(500),
        unique=True
    )


    source = Column(
        String(50)
    )


    created_at = Column(
        DateTime,
        server_default=func.now()
    )