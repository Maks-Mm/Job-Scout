#backend/app/collectors/__init__.py

from .adzuna import AdzunaCollector
from .arbeitnow import ArbeitnowCollector
from .jooble import JoobleCollector
from .arbeitsagentur import ArbeitsagenturCollector

collectors = [
    AdzunaCollector(),
    ArbeitnowCollector(),
    JoobleCollector(),
    ArbeitsagenturCollector(),
]