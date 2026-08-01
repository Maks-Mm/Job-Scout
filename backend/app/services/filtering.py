#backend/app/services/filtering.py

from pydantic import BaseModel
from typing import Optional
from collections import Counter
import re


class JobFilter(BaseModel):
    country: Optional[str] = "Germany"
    city: str
    language: Optional[str] = "de"
    keywords: Optional[str] = None
    job_category: Optional[str] = None
    employment_type: Optional[str] = None
    source: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None


CATEGORY_KEYWORDS = {
    "buero": [
        "büro", "office", "sachbearbeiter", "verwaltung",
        "assistenz", "sekretär", "empfang", "backoffice",
        "bürokaufmann", "bürokauffrau", "kaufmann", "kauffrau",
        "administration", "administrative"
    ],
    "verkauf": [
        "verkauf", "einzelhandel", "kasse", "cashier",
        "shop", "verkäufer", "vertrieb", "sales",
        "handel", "filiale", "store", "retail"
    ],
    "gastronomie": [
        "gastronomie", "restaurant", "kellner", "service",
        "bar", "küche", "koch", "hotel",
        "zimmermädchen", "gast", "catering",
        "lebensmittel", "waiter", "chef", "cook"
    ],
    "logistik": [
        "lager", "lagerist", "lagerhelfer", "lagerarbeiter",
        "warehouse", "logistik", "logistics", "transport",
        "supply chain", "distribution", "versand",
        "kommissionierer", "kommissionierung", "picker", "packer",
        "fulfillment", "disponent", "dispatcher", "fahrer",
        "lieferfahrer", "zusteller", "kurier", "forklift",
        "stapler", "staplerfahrer", "umschlag"
    ],
    "bau": [
        "bau", "baustelle", "handwerker", "produktion",
        "produktionshelfer", "montage", "elektriker",
        "schlosser", "mechaniker", "bauarbeiter",
        "handwerk", "installateur", "metall",
        "construction", "production"
    ],
    "kundenservice": [
        "kundenservice", "call center", "support",
        "customer service", "telefon", "service",
        "beratung", "hotline", "kundenbetreuung"
    ],
    "pflege": [
        "pflege", "krankenpflege", "altenpflege",
        "pfleger", "krankenschwester", "pflegehelfer",
        "gesundheit", "sozial", "betreuung",
        "medizin", "nurse", "caregiver"
    ],
    "it": [
        "software", "developer", "entwickler",
        "frontend", "backend", "fullstack",
        "programmierer", "web", "system",
        "administrator", "technik", "digital",
        "devops", "cloud", "engineer", "python",
        "java", "react", "javascript", "typescript",
        "c#", ".net", "sql"
    ],
    "ausbildung": [
        "ausbildung", "azubi", "apprentice",
        "lehre", "auszubildender", "lehrling"
    ],
    "praktikum": [
        "praktikum", "intern", "trainee",
        "volontariat", "werkstudent", "student"
    ],
    "mini": [
        "minijob", "nebenjob", "aushilfe",
        "520", "geringfügig", "teilzeit"
    ],
    "weitere": [
        "sonstige", "divers", "allgemein"
    ],
}


# Country normalization mapping
COUNTRY_NORMALIZE = {
    "de": "germany",
    "germany": "germany",
    
    "at": "austria",
    "austria": "austria",
    
    "ch": "switzerland",
    "switzerland": "switzerland",
    "schweiz": "switzerland",
    
    "li": "switzerland",
    "liechtenstein": "switzerland",
}


def contains_keyword(text: str, keywords: list[str]) -> bool:
    text = text.lower()

    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, text):
            return True

    return False


def filter_jobs(jobs: list, filters: JobFilter):
    """Filter jobs based on criteria"""

    result = []

    # Per-stage rejection counters, keyed by source, so we can see
    # exactly which check is eliminating jobs for a given source.
    rejected_by_stage = Counter()
    rejected_samples = {}  # stage -> up to 3 example (source, title) tuples

    def reject(stage, job):
        rejected_by_stage[stage] += 1
        if stage not in rejected_samples:
            rejected_samples[stage] = []
        if len(rejected_samples[stage]) < 3:
            rejected_samples[stage].append(
                (job.get("source"), job.get("title"), job.get("country"), job.get("category"))
            )

    print("=" * 50)
    print("DEBUG FILTER")
    print(filters.model_dump())
    print("=" * 50)

    for job in jobs:
        if not job or not isinstance(job, dict):
            continue

        # Country
        if filters.country:
            # Normalize the wanted country
            wanted_country = COUNTRY_NORMALIZE.get(
                filters.country.lower(),
                filters.country.lower()
            )
            
            # Normalize the job country
            job_country = COUNTRY_NORMALIZE.get(
                str(job.get("country") or "").lower(),
                str(job.get("country") or "").lower()
            )
            
            # Skip if job_country is empty or doesn't match wanted_country
            if job_country and job_country != wanted_country:
                reject("country", job)
                continue

        # Language
        if filters.language:
            job_language = str(job.get("language") or "de")
            if job_language.lower() != filters.language.lower():
                reject("language", job)
                continue

        # Keywords
        if filters.keywords:
            text = (
                f"{job.get('title','')} "
                f"{job.get('company','')} "
                f"{job.get('description','')}"
            ).lower()

            if filters.keywords.lower() not in text:
                reject("keywords", job)
                continue

        # Category
        if filters.job_category and filters.job_category != "all":

            category_words = CATEGORY_KEYWORDS.get(filters.job_category, [])

            searchable_text = " ".join([
                str(job.get("title", "")),
                str(job.get("company", "")),
                str(job.get("description", "")),
                str(job.get("category", "")),
            ]).lower()

            if not contains_keyword(searchable_text, category_words):
                reject("category", job)
                continue

        # Source
        if filters.source:
            if job.get("source") != filters.source:
                reject("source", job)
                continue

        # Salary
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        if (
            filters.min_salary is not None
            and filters.min_salary > 0
            and salary_min is not None
            and salary_min < filters.min_salary
        ):
            reject("min_salary", job)
            continue

        if (
            filters.max_salary is not None
            and filters.max_salary > 0
            and salary_max is not None
            and salary_max > filters.max_salary
        ):
            reject("max_salary", job)
            continue

        result.append(job)

    # TEMP DEBUG — remove once the empty-result cause is confirmed
    print(f"[filter_jobs] kept={len(result)} rejected_by_stage={dict(rejected_by_stage)}")
    for stage, samples in reversed(list(rejected_samples.items())):
        print(f"[filter_jobs] sample rejects for stage='{stage}':")
        for source, title, country, category in samples:
            print(f"    source={source!r} country={country!r} category={category!r} title={title!r}")

    return result


def categorize_job(job: dict) -> str:
    """Automatically categorize a job."""

    text = " ".join([
        str(job.get("title", "")),
        str(job.get("description", "")),
        str(job.get("company", "")),
        str(job.get("category", "")),
    ]).lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if contains_keyword(text, keywords):
            return category

    return "weitere"