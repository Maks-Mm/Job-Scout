#backend/app/collectors/__init__.py

from .adzuna import AdzunaCollector
from .indeed import IndeedCollector
from .jooble import JoobleCollector
from .stepstone import StepstoneCollector


collectors = [

    AdzunaCollector(),

    IndeedCollector(),

    JoobleCollector(),

    StepstoneCollector()

]