#backend/app/scraper/indeed.py
def scrape_indeed(city: str):
    """Fake scraper — replace with real API calls in Phase 2."""
    return [
        {
            "title": "Python Developer",
            "company": "Example GmbH",
            "city": city,
            "country": "Germany",
            "salary_min": 57000,
            "salary_max": 75000,
            "currency": "EUR",
            "category": "IT & Software",
            "description": "We are looking for a Python developer with FastAPI experience.",
            "url": "https://indeed.de/jobs/python-developer-munich-001",
            "source": "Indeed"
        },
        {
            "title": "Electronics Technician",
            "company": "Example GmbH",
            "city": city,
            "country": "Germany",
            "salary_min": 38000,
            "salary_max": 48000,
            "currency": "EUR",
            "category": "Installation & Maintenance",
            "description": "Seeking an electronics technician for industrial maintenance.",
            "url": "https://indeed.de/jobs/electronics-technician-munich-002",
            "source": "Indeed"
        },
        {
            "title": "Nurse / Healthcare Professional",
            "company": "Example Klinik",
            "city": city,
            "country": "Germany",
            "salary_min": 46000,
            "salary_max": 55000,
            "currency": "EUR",
            "category": "Health & Social Care",
            "description": "Looking for qualified nursing professionals.",
            "url": "https://indeed.de/jobs/nurse-munich-003",
            "source": "Indeed"
        },
        {
            "title": "Logistics Manager",
            "company": "Example Logistik",
            "city": city,
            "country": "Germany",
            "salary_min": 40000,
            "salary_max": 50000,
            "currency": "EUR",
            "category": "Administration & Logistics",
            "description": "Managing warehouse and logistics operations.",
            "url": "https://indeed.de/jobs/logistics-manager-munich-004",
            "source": "Indeed"
        },
        {
            "title": "Sales Manager",
            "company": "Example AG",
            "city": city,
            "country": "Germany",
            "salary_min": 54000,
            "salary_max": 65000,
            "currency": "EUR",
            "category": "Sales & Management",
            "description": "Driving B2B sales in the DACH region.",
            "url": "https://indeed.de/jobs/sales-manager-munich-005",
            "source": "Indeed"
        },
        {
            "title": "Teacher / Educator",
            "company": "Example School",
            "city": city,
            "country": "Germany",
            "salary_min": 46000,
            "salary_max": 55000,
            "currency": "EUR",
            "category": "Education & Instruction",
            "description": "Teaching position at a state-recognized school.",
            "url": "https://indeed.de/jobs/teacher-munich-006",
            "source": "Indeed"
        },
    ]
    