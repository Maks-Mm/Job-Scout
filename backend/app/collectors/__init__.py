# backend/app/collectors/__init__.py

from .adzuna import AdzunaCollector
from .arbeitnow import ArbeitnowCollector
from .jooble import JoobleCollector
from .arbeitsagentur import ArbeitsagenturCollector
from .kleinanzeigen import KleinanzeigenCollector
from .stepstone import StepStoneCollector
from .stellenanzeigen import StellenanzeigenCollector

collectors = [
    AdzunaCollector(),
    ArbeitnowCollector(),
    JoobleCollector(),
    ArbeitsagenturCollector(),
    KleinanzeigenCollector(),
    StepStoneCollector(),
    StellenanzeigenCollector(),
]