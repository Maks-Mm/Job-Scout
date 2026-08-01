#backend/app/collectors/switzerland/_init__.py

from .jobs_ch import JobsCHCollector
from .jobscout24 import JobScout24Collector
from .arbeitgeber_ch import ArbeitgeberCHCollector

__all__ = [
    "JobsCHCollector",
    "JobScout24Collector",
    "ArbeitgeberCHCollector",
]