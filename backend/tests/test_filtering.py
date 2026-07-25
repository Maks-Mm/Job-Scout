#backend/tests/test_filtering.py

from app.services.filtering import JobFilter, filter_jobs


def test_min_salary_keeps_jobs_without_known_salary_data():
    filters = JobFilter(city="Munich", min_salary=150)
    jobs = [
        {"title": "Job A", "salary_min": None, "salary_max": 5000},
        {"title": "Job B", "salary_min": 200, "salary_max": 5000},
    ]

    result = filter_jobs(jobs, filters)

    assert len(result) == 2
    assert [job["title"] for job in result] == ["Job A", "Job B"]


def test_max_salary_filters_out_jobs_above_threshold():
    filters = JobFilter(city="Munich", max_salary=10000)
    jobs = [
        {"title": "Job A", "salary_min": 100, "salary_max": 12000},
        {"title": "Job B", "salary_min": 100, "salary_max": 9000},
    ]

    result = filter_jobs(jobs, filters)

    assert len(result) == 1
    assert result[0]["title"] == "Job B"
