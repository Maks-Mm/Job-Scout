# backend/app/core/config.py
import os
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./jobs.db"
)


ADZUNA_APP_ID = os.getenv(
    "ADZUNA_APP_ID"
)


ADZUNA_API_KEY = os.getenv(
    "ADZUNA_API_KEY"
)