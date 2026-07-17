#backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.jobs import router
from app.workers.scheduler import start_scheduler
import os

app = FastAPI()

# CORS middleware - WICHTIG für Render!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dein-frontend-name.onrender.com",  # DEINE ECHTE FRONTEND URL
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def startup():  
     start_scheduler()

@app.get("/")
def root():
    return {"status": "Job Scout running"}