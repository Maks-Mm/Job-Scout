from typing import List
from app.models.job import Job


def get_jobs_from_db(city: str = None) -> List[dict]:
    # Placeholder: implement real DB queries using SQLAlchemy sessions
    return [
        {
            "id": 1,
            "title": "DB Example Job",
            "company": "DB Co",
            "city": city or "Munich",
            "salary": "400€/month",
            "url": "https://example.com",
            "source": "DB",
        }
    ]
