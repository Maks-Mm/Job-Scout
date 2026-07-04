#backend/app/schemas/job.py

from pydantic import BaseModel


class JobResponse(BaseModel):

    id:int

    title:str

    company:str | None

    city:str | None

    salary_min:float | None

    salary_max:float | None

    source:str

    url:str


    class Config:

        from_attributes=True