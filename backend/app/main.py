# backend/app/main.py

from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware

# ── CRITICAL: import all models FIRST so SQLAlchemy registers every
# mapper before any route or query touches the DB. ──────────────────────
import app.models  # noqa: F401  — triggers app/models/__init__.py

from app.api.routes.jobs import router as jobs_router
from app.api.routes.users import router as users_router
from app.workers.scheduler import start_scheduler
from app.core.migrations import ensure_user_schema

app = FastAPI()

ensure_user_schema()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jobs-scout-frontend.onrender.com",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.include_router(users_router)


@app.on_event("startup")
def startup():
    if os.getenv("START_SCHEDULER") == "1":
        try:
            start_scheduler()
            print("Scheduler started successfully")
        except Exception as e:
            print(f"Failed to start scheduler on startup: {e}")
    else:
        print("Scheduler not started (START_SCHEDULER!=1)")


@app.get("/")
def root():
    return {"status": "Job Scout running"}