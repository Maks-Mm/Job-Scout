#backend/app/main.py

#backend/app/main.py

from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.jobs import router
from app.workers.scheduler import start_scheduler

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jobs-scout-frontend.onrender.com",  # Deine Frontend URL
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def startup():  
    # Only start the background scheduler when explicitly enabled.
    # This avoids startup crashes on hosts where background jobs cause issues.
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