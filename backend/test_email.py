#backend/test_email.py


from app.notifications.email_service import send_job_email
print("TEST START")
jobs = [
    {
        "title": "Python Backend Developer",
        "company": "Siemens AG",
        "city": "München",
        "salary_min": 4500,
        "salary_max": 6200,
        "description": "Wir suchen einen erfahrenen Python Backend Developer mit FastAPI, PostgreSQL und Docker.",
        "url": "https://example.com/job1",
        "source": "StepStone"
    },
    {
        "title": "Lagerhelfer",
        "company": "Amazon",
        "city": "Berlin",
        "salary_min": 2500,
        "salary_max": 3100,
        "description": "Kommissionieren, Verpacken und Versand.",
        "url": "https://example.com/job2",
        "source": "Arbeitsagentur"
    },
    {
        "title": "Logistik Manager",
        "company": "DHL",
        "city": "Hamburg",
        "salary_min": 4200,
        "salary_max": 5200,
        "description": "Leitung eines Logistikteams.",
        "url": "https://example.com/job3",
        "source": "Jooble"
    }
]

send_job_email(
    "maxfilawwwrest@gmail.com",
    jobs
)

print("MAIL SENT")