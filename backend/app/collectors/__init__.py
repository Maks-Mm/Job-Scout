#backend/app/collectors/__init__.py

from .adzuna import AdzunaCollector
from .arbeitnow import ArbeitnowCollector
from .jooble import JoobleCollector

collectors = [
    AdzunaCollector(),
    ArbeitnowCollector(),
    JoobleCollector(),
]