def scrape_indeed(city: str):
    """Fake scraper returning a sample job list for the given city.

    Replace with real scraping logic (requests/httpx + BeautifulSoup) later.
    """
    return [
        {
            "id": 1,
            "title": "Warehouse Worker",
            "company": "Example GmbH",
            "city": city,
            "salary": "450€/month",
            "url": "https://indeed.de",
            "source": "Indeed",
        }
    ]
