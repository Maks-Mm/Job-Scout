#backend/app/collectors/collector_registry.py


# backend/app/collectors/collector_registry.py

from typing import List, Optional

from .base import JobCollector

# Germany
from .germany.arbeitsagentur import ArbeitsagenturCollector
from .germany.stepstone import StepStoneCollector
from .germany.stellenanzeigen import StellenanzeigenCollector
from .germany.kleinanzeigen import KleinanzeigenCollector

# Austria
try:
    from .austria.ams import AMSCollector
    from .austria.karriere_at import KarriereATCollector
    from .austria.willhaben import WillhabenCollector
    AUSTRIA_AVAILABLE = True
except Exception as e:
    print("Austria collectors error:", e)
    AUSTRIA_AVAILABLE = False

# Switzerland
try:
    from .switzerland.jobs_ch import JobsCHCollector
    from .switzerland.jobscout24 import JobScout24Collector
    from .switzerland.arbeitgeber_ch import ArbeitgeberCHCollector
    SWISS_AVAILABLE = True
except Exception as e:
    print("Swiss collectors error:", e)
    SWISS_AVAILABLE = False

# Belgium - NEU
try:
    from .belgien.eURES import EURESCollector
    from .belgien.indeedBelgien import IndeedBelgiumCollector
    from .belgien.stepStoneBelgien import StepStoneBelgiumCollector
    BELGIUM_AVAILABLE = True
except Exception as e:
    print("Belgium collectors error:", e)
    BELGIUM_AVAILABLE = False

# Shared
from .shared.adzuna import AdzunaCollector
from .shared.arbeitnow import ArbeitnowCollector
from .shared.jooble import JoobleCollector


COUNTRY_ALIASES = {
    "germany": "germany",
    "de": "germany",

    "austria": "austria",
    "at": "austria",

    "switzerland": "switzerland",
    "schweiz": "switzerland",
    "ch": "switzerland",

    "liechtenstein": "switzerland",
    "li": "switzerland",

    "luxembourg": "luxembourg",

    # NEU: Belgien
    "belgium": "belgium",
    "belgien": "belgium",
    "be": "belgium",
}


def get_collectors(country_name: str) -> List[JobCollector]:

    country = COUNTRY_ALIASES.get(
        (country_name or "").lower(),
        "germany"
    )

    shared = [
        AdzunaCollector(),
        JoobleCollector(),
    ]

    if country == "germany":
        collectors = [
            ArbeitsagenturCollector(),
            StepStoneCollector(),
            StellenanzeigenCollector(),
            KleinanzeigenCollector(),
            ArbeitnowCollector(),
        ] + shared

    elif country == "austria":
        collectors = shared
        if AUSTRIA_AVAILABLE:
            collectors = [
                AMSCollector(),
                KarriereATCollector(),
                WillhabenCollector(),
            ] + shared

    elif country == "switzerland":
        collectors = shared
        if SWISS_AVAILABLE:
            collectors = [
                JobsCHCollector(),
                JobScout24Collector(),
                ArbeitgeberCHCollector(),
            ] + shared

    # NEU: Belgien
    elif country == "belgium":
        collectors = shared
        if BELGIUM_AVAILABLE:
            collectors = [
                EURESCollector(),
                IndeedBelgiumCollector(),
                StepStoneBelgiumCollector(),
            ] + shared

    else:
        collectors = shared

    print(
        f"[Registry] {country_name} -> "
        f"{[c.source for c in collectors]}"
    )

    return collectors


def get_collector_by_source(source_name: str):
    mapping = {
        # Germany
        "Arbeitsagentur": ArbeitsagenturCollector,
        "StepStone": StepStoneCollector,
        "Stellenanzeigen": StellenanzeigenCollector,
        "Kleinanzeigen": KleinanzeigenCollector,

        # Austria
        "AMS": AMSCollector,
        "Karriere.at": KarriereATCollector,
        "Willhaben": WillhabenCollector,

        # Switzerland
        "jobs.ch": JobsCHCollector,
        "JobScout24": JobScout24Collector,
        "Arbeitgeber.ch": ArbeitgeberCHCollector,

        # NEU: Belgien
        "EURES Belgium": EURESCollector,
        "Indeed Belgium": IndeedBelgiumCollector,
        "StepStone Belgium": StepStoneBelgiumCollector,

        # Shared
        "Adzuna": AdzunaCollector,
        "Arbeitnow": ArbeitnowCollector,
        "Jooble": JoobleCollector,
    }

    collector = mapping.get(source_name)
    if collector:
        return collector()

    return None


def get_all_collectors():
    countries = [
        "germany",
        "austria",
        "switzerland",
        "belgium",  # NEU
    ]

    result = []
    seen = set()

    for country in countries:
        for collector in get_collectors(country):
            if collector.source not in seen:
                seen.add(collector.source)
                result.append(collector)

    return result