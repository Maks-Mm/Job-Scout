from pydantic import BaseModel


class Job(BaseModel):
    id: int
    title: str
    company: str
    city: str
    salary: str
    url: str
    source: str
