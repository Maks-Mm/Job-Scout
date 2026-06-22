from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.jobs import router as jobs_router
from app.api.core.database import Base, engine

import app.api.models.job  # registers models with SQLAlchemy


app = FastAPI(title="Job Scout API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# create DB tables
Base.metadata.create_all(bind=engine)


app.include_router(jobs_router)


@app.get("/")
async def root():
    return {"status": "running"}
