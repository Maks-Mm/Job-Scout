#backend/tests/test_alert_window.py
from datetime import datetime, timedelta, timezone

from app.workers.job_notifier import _filter_recent_jobs


def test_filter_recent_jobs_keeps_only_jobs_within_last_24_hours():
    now = datetime.now(timezone.utc)

    jobs = [
        {"url": "old", "date": (now - timedelta(hours=30)).isoformat()},
        {"url": "recent", "date": (now - timedelta(hours=2)).isoformat()},
        {"url": "future", "date": (now + timedelta(hours=2)).isoformat()},
        {"url": "no-date", "title": "missing date"},
    ]

    result = _filter_recent_jobs(jobs, 24)

    assert [job["url"] for job in result] == ["recent"]
