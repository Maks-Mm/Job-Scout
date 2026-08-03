# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    # ... other fields
    alerts_enabled = Column(Boolean, default=True)
    country = Column(String, default="germany")
    city = Column(String)
    keywords = Column(String)  # Comma-separated keywords
    
    user_jobs = relationship("UserJob", back_populates="user")