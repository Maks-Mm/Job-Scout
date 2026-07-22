# backend/app/services/filtering.py

from pydantic import BaseModel
from typing import Optional


class JobFilter(BaseModel):
    city: str
    keywords: Optional[str] = None
    job_category: Optional[str] = None
    employment_type: Optional[str] = None
    source: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None


CATEGORY_KEYWORDS = {
    "buero": [
        "büro", "office", "sachbearbeiter", "verwaltung",
        "assistenz", "sekretär", "empfang"
    ],
    "verkauf": [
        "verkauf", "einzelhandel", "kasse", "cashier",
        "shop", "verkäufer"
    ],
    "gastronomie": [
        "gastronomie", "restaurant", "kellner", "service",
        "bar", "küche", "koch", "hotel", "zimmermädchen"
    ],
    "logistik": [
        "lager", "logistik", "warehouse", "kommissionierer",
        "picker", "packer", "versand", "stapler",
        "fahrer", "lieferfahrer"
    ],
    "bau": [
        "bau", "baustelle", "handwerker", "produktion",
        "produktionshelfer", "montage", "elektriker",
        "schlosser", "mechaniker"
    ],
    "kundenservice": [
        "kundenservice", "call center", "support",
        "customer service", "telefon"
    ],
    "pflege": [
        "pflege", "krankenpflege", "altenpflege",
        "pfleger", "krankenschwester",
        "pflegehelfer"
    ],
    "it": [
        "it", "software", "developer", "entwickler",
        "frontend", "backend", "fullstack",
        "administrator"
    ],
    "ausbildung": [
        "ausbildung", "azubi", "apprentice"
    ],
    "praktikum": [
        "praktikum", "intern"
    ],
    "mini": [
        "minijob", "nebenjob", "aushilfe", "520"
    ],
}


def filter_jobs(jobs: list, filters: JobFilter):

    print("filter_jobs called")
    print(filters.model_dump())

    result = []

    for job in jobs:

        # Keyword
        if filters.keywords:

            text = (
                f"{job.get('title', '')} "
                f"{job.get('company', '')}"
            ).lower()

            if filters.keywords.lower() not in text:
                continue

        # Job category
        if filters.job_category and filters.job_category != "all":

            category_words = CATEGORY_KEYWORDS.get(filters.job_category, [])

            # Debug: zeigt welche Felder ein Job überhaupt hat
            print(job.keys())
            print(job.get("title"))

            text = (
                f"{job.get('title', '')} "
                f"{job.get('company', '')} "
                f"{job.get('description', '')}"
            ).lower()

            if not any(word in text for word in category_words):
                continue

        # Source
        if filters.source:

            if job.get("source") != filters.source:
                continue

        # Salary
        if filters.min_salary:
            salary_max = job.get("salary_max")
            if salary_max is not None:
                if salary_max < filters.min_salary:
                    continue

        if filters.max_salary:
            salary_min = job.get("salary_min")
            if salary_min is not None:
                if salary_min > filters.max_salary:
                    continue

        result.append(job)

    return result