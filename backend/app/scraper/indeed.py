def scrape_indeed(city: str):
    """Fake scraper returning a sample of the most in-demand job categories for the given city."""
    return [
        {
            "id": 1,
            "title": "Electronics Technician (Elektroniker)",
            "company": "Example GmbH",
            "city": city,
            "salary": "€38,000 - €48,000/year",
            "url": "https://indeed.de",
            "source": "Indeed",
            "category": "Installation & Maintenance"
        },
        {
            "id": 2,
            "title": "Sales Manager / Operations Manager",
            "company": "Example AG",
            "city": city,
            "salary": "€54,000 - €65,000/year",
            "url": "https://indeed.de",
            "source": "Indeed",
            "category": "Sales & Management"
        },
        {
            "id": 3,
            "title": "Nurse / Healthcare Professional (Pflegefachkraft)",
            "company": "Example Klinik",
            "city": city,
            "salary": "€46,000 - €55,000/year",
            "url": "https://indeed.de",
            "source": "Indeed",
            "category": "Health & Social Care"
        },
        {
            "id": 4,
            "title": "Logistics / Warehouse Manager",
            "company": "Example Logistik",
            "city": city,
            "salary": "€40,000 - €50,000/year",
            "url": "https://indeed.de",
            "source": "Indeed",
            "category": "Administration & Logistics"
        },
        {
            "id": 5,
            "title": "IT Manager / Software Developer",
            "company": "Example Tech",
            "city": city,
            "salary": "€57,000 - €75,000/year",
            "url": "https://indeed.de",
            "source": "Indeed",
            "category": "IT & Software"
        },
        {
            "id": 6,
            "title": "Teacher / Educator (Pädagogische Fachkraft)",
            "company": "Example School",
            "city": city,
            "salary": "€46,000 - €55,000/year",
            "url": "https://indeed.de",
            "source": "Indeed",
            "category": "Education & Instruction"
        }
    ]