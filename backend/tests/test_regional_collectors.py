import httpx
import pytest

from app.collectors.austria.ams import AMSCollector
from app.collectors.switzerland.jobs_ch import JobsCHCollector
from app.collectors.switzerland.jobscout24 import JobScout24Collector
from app.services.filtering import JobFilter


@pytest.mark.parametrize(
    "collector_cls",
    [AMSCollector, JobsCHCollector, JobScout24Collector],
)
def test_regional_collectors_return_jobs_when_http_fails(monkeypatch, collector_cls):
    def fail_get(*args, **kwargs):
        raise httpx.RequestError("simulated network failure")

    monkeypatch.setattr(httpx, "get", fail_get)

    filters = JobFilter(
        country="Austria" if collector_cls is AMSCollector else "Switzerland",
        city="Vienna" if collector_cls is AMSCollector else "Zurich",
        keywords="developer",
        language="de",
    )

    collector = collector_cls()
    jobs = collector.fetch_jobs(filters)

    assert jobs, f"{collector.source} should return fallback jobs"
    assert jobs[0]["source"] == collector.source
    assert jobs[0]["title"]
