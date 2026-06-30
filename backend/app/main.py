from fastapi import FastAPI

from app.core.database import (
    Base,
    engine
)

from app.api.routes.jobs import router


#import app.models.job

#from app.models.job import Job

import app.models



Base.metadata.create_all(
    bind=engine
)



app = FastAPI(
    title="Job Scout API"
)



app.include_router(
    router,
    prefix="/api"
)



@app.get("/")
def root():

    return {
        "status":"running"
    }