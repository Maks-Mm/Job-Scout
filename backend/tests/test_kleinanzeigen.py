#backend/tests/test_kleinanzeigen.py

from app.collectors.kleinanzeigen import KleinanzeigenCollector


def test_kleinanzeigen_returns_source_name(monkeypatch):

    class FakeResponse:
        text = """
        <article>
            <a href="/s-anzeige/test-job">
                <span class="ellipsis">
                    Bürohilfe Teilzeit
                </span>
            </a>
        </article>
        """

        def raise_for_status(self):
            pass


    monkeypatch.setattr(
        "requests.get",
        lambda *args, **kwargs: FakeResponse()
    )


    collector = KleinanzeigenCollector()

    filter = type(
        "Filter",
        (),
        {
            "city": "Munich",
            "keywords": "Büro",
            "employment_type": "parttime",
        },
    )

    jobs = collector.fetch_jobs(filter)

    assert len(jobs) == 1
    assert jobs[0]["source"] == "Kleinanzeigen"