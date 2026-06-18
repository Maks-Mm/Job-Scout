# Job Scout — Backend (Modular Monolith)

Quick scaffold for a FastAPI backend used by the Next.js frontend.

Run locally (Python venv):

```powershell
cd "backend"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Or using Docker Compose:

```powershell
cd "backend"
docker compose up --build
```

Endpoints:

- `GET /api/jobs?city=Munich` — returns a sample job list (fake scraper)

Replace `app/scraper/indeed.py` with real scraping logic and wire DB in `app/db`.
