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
    result = []

    for job in jobs:
        if not job:
            continue

        if not isinstance(job, dict):
            continue

        if filters.keywords:
            text = (
                f"{job.get('title', '')} "
                f"{job.get('company', '')}"
            ).lower()

            if filters.keywords.lower() not in text:
                continue

        if filters.job_category and filters.job_category != "all":
            category_words = CATEGORY_KEYWORDS.get(filters.job_category, [])

            text = (
                f"{job.get('title', '')} "
                f"{job.get('company', '')} "
                f"{job.get('description', '')}"
            ).lower()

            if not any(word in text for word in category_words):
                continue

        if filters.source:
            if job.get("source") != filters.source:
                continue

        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        if filters.min_salary is not None and filters.min_salary > 0:
            if salary_min is not None and salary_min < filters.min_salary:
                continue

        if filters.max_salary is not None and filters.max_salary > 0:
            if salary_max is not None and salary_max > filters.max_salary:
                continue

        result.append(job)

    return result