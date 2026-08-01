#backend/app/core/regions.py

SUPPORTED_REGIONS = {
    "Germany": {
        "language": "de",
        "currency": "EUR",
        "cities": [
            "Berlin",
            "Munich",
            "Hamburg",
            "Cologne",
            "Frankfurt",
            "Stuttgart",
            "Düsseldorf",
            "Leipzig",
        ],
    },
    "Austria": {
        "language": "de",
        "currency": "EUR",
        "cities": [
            "Vienna",
            "Graz",
            "Linz",
            "Salzburg",
            "Innsbruck",
        ],
    },
    "Switzerland": {
        "language": "de",
        "currency": "CHF",
        "cities": [
            "Zurich",
            "Bern",
            "Basel",
            "Lucerne",
            "St. Gallen",
        ],
    },
    "Liechtenstein": {
        "language": "de",
        "currency": "CHF",
        "cities": ["Vaduz"],
    },
    "Luxembourg": {
        "language": "de",
        "currency": "EUR",
        "cities": ["Luxembourg"],
    },
}


def get_supported_regions():
    return list(SUPPORTED_REGIONS.keys())


def get_region_settings(country: str | None):
    if not country:
        return SUPPORTED_REGIONS.get("Germany", {})
    return SUPPORTED_REGIONS.get(country, SUPPORTED_REGIONS.get("Germany", {}))
