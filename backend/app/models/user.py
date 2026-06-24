from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.api.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())