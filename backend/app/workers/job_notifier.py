# backend/app/workers/job_notifier.py

from datetime import datetime, timedelta, timezone

from app.services.filtering import filter_jobs, JobFilter
from app.notifications.email_service import send_job_email
from app.core.database import SessionLocal
from app.models.user import User
from app.models.job import Job
from app.models.user_job import UserJob


ALERT_WINDOW_HOURS = 24
MAX_JOBS_PER_EMAIL = 20


def _parse_job_datetime(value) -> datetime | None:
    if not value:
        return None

    try:
        if isinstance(value, datetime):
            dt = value

        elif hasattr(value, "year") and hasattr(
            value,
            "month",
        ) and hasattr(
            value,
            "day",
        ):
            dt = datetime(
                value.year,
                value.month,
                value.day,
            )

        elif isinstance(value, str):
            raw = value.strip()

            if not raw:
                return None

            raw = raw.replace(
                "Z",
                "+00:00",
            )

            dt = datetime.fromisoformat(raw)

        else:
            return None

        if dt.tzinfo is None:
            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt.astimezone(
            timezone.utc
        )

    except Exception:
        return None


def _get_job_datetime(
    job: dict,
) -> datetime | None:
    return _parse_job_datetime(
        job.get("date")
        or job.get("created_at")
        or job.get("posted_at")
    )


def _filter_recent_jobs(
    jobs: list[dict],
    hours: int = ALERT_WINDOW_HOURS,
) -> list[dict]:
    now = datetime.now(
        timezone.utc
    )

    cutoff = (
        now
        - timedelta(hours=hours)
    )

    recent_jobs = []
    skipped_without_date = 0

    for job in jobs:
        published_at = _get_job_datetime(
            job
        )

        if published_at is None:
            skipped_without_date += 1
            continue

        if cutoff <= published_at <= now:
            recent_jobs.append(job)

    print(
        "[Notifier] Recent-job window: "
        f"{len(recent_jobs)} jobs within last "
        f"{hours}h"
    )

    if skipped_without_date:
        print(
            "[Notifier] Skipped "
            f"{skipped_without_date} jobs "
            "without valid publication date"
        )

    return recent_jobs


def check_recent_jobs(
    collected_jobs: list[dict],
):
    print(
        "[Notifier] Evaluating "
        f"{len(collected_jobs)} collected jobs"
    )

    if not collected_jobs:
        print(
            "[Notifier] No collected jobs"
        )
        return

    recent_jobs = _filter_recent_jobs(
        collected_jobs,
        ALERT_WINDOW_HOURS,
    )

    if not recent_jobs:
        print(
            "[Notifier] No jobs inside "
            f"the last {ALERT_WINDOW_HOURS} hours"
        )
        return

    # Deduplicate again before user evaluation.
    unique_jobs: dict[str, dict] = {}

    for job in recent_jobs:
        url = job.get("url")

        if not url:
            continue

        unique_jobs[url] = job

    recent_jobs = list(
        unique_jobs.values()
    )

    print(
        "[Notifier] Unique recent jobs: "
        f"{len(recent_jobs)}"
    )

    users = get_users_with_alerts()

    print(
        "[Notifier] Found "
        f"{len(users)} eligible users"
    )

    if not users:
        print(
            "[Notifier] No eligible users"
        )
        return

    for user in users:
        process_user(
            user,
            recent_jobs,
        )


def check_new_jobs(
    new_jobs: list[dict],
):
    """
    Backward-compatible wrapper.
    """
    check_recent_jobs(
        new_jobs
    )


def process_user(
    user,
    recent_jobs: list[dict],
):
    print(
        f"[Notifier] Processing {user.email} "
        f"city={user.city} "
        f"keywords={user.keywords} "
        f"employment_type={user.employment_type} "
        f"salary={user.min_salary}-{user.max_salary}"
    )

    try:
        filter_params = JobFilter(
            country=getattr(
                user,
                "country",
                "Germany",
            ) or "Germany",

            city=getattr(
                user,
                "city",
                "",
            ) or "",

            keywords=getattr(
                user,
                "keywords",
                "",
            ) or "",

            language=getattr(
                user,
                "language",
                "de",
            ) or "de",

            employment_type=getattr(
                user,
                "employment_type",
                "all",
            ) or "all",

            job_category=getattr(
                user,
                "job_category",
                "all",
            ) or "all",

            min_salary=getattr(
                user,
                "min_salary",
                None,
            ),

            max_salary=getattr(
                user,
                "max_salary",
                None,
            ),
        )

        print(
            "[Notifier] Filter: "
            f"{filter_params.model_dump()}"
        )

        filtered = filter_jobs(
            recent_jobs,
            filter_params,
        )

        print(
            "[Notifier] Matching recent jobs: "
            f"{len(filtered)}"
        )

        if not filtered:
            print(
                "[Notifier] No matching jobs "
                f"for {user.email}"
            )
            return

        unsent = remove_already_sent(
            user,
            filtered,
        )

        print(
            "[Notifier] Matching but unsent: "
            f"{len(unsent)}"
        )

        if not unsent:
            print(
                "[Notifier] All matching recent jobs "
                f"already sent to {user.email}"
            )
            return

        unsent = _sort_by_freshness(
            unsent
        )

        # Only these jobs are actually sent.
        jobs_to_send = unsent[
            :MAX_JOBS_PER_EMAIL
        ]

        print(
            "[Notifier] Sending "
            f"{len(jobs_to_send)} jobs "
            f"to {user.email}"
        )

        sent = send_job_email(
            receiver=user.email,
            jobs=jobs_to_send,
            unsubscribe_token=user.unsubscribe_token,
            user_filters={
                "city": getattr(
                    user,
                    "city",
                    "",
                ),
                "country": getattr(
                    user,
                    "country",
                    "Germany",
                ),
                "employment_type": getattr(
                    user,
                    "employment_type",
                    None,
                ),
                "min_salary": getattr(
                    user,
                    "min_salary",
                    None,
                ),
                "max_salary": getattr(
                    user,
                    "max_salary",
                    None,
                ),
                "keywords": getattr(
                    user,
                    "keywords",
                    "",
                ),
            },
        )

        print(
            "[Notifier] send_job_email result: "
            f"{sent}"
        )

        if sent is True:
            save_sent_jobs(
                user,
                jobs_to_send,
            )
        else:
            print(
                "[Notifier] Email failed for "
                f"{user.email}; "
                "jobs remain unsent"
            )

    except Exception as e:
        print(
            "[Notifier] Error processing "
            f"{user.email}: {e}"
        )


def _sort_by_freshness(
    jobs: list[dict],
) -> list[dict]:
    def _date_key(job: dict):
        published_at = _get_job_datetime(
            job
        )

        if published_at is None:
            return datetime.min.replace(
                tzinfo=timezone.utc
            )

        return published_at

    return sorted(
        jobs,
        key=_date_key,
        reverse=True,
    )


def get_users_with_alerts():
    db = SessionLocal()

    try:
        users = (
            db.query(User)
            .filter(
                User.alerts_enabled.is_(True),
                User.consent_given.is_(True),
                User.verified_email.is_(True),
            )
            .all()
        )

        return users

    except Exception as e:
        print(
            "[Notifier] Error fetching users: "
            f"{e}"
        )
        return []

    finally:
        db.close()


def remove_already_sent(
    user,
    jobs: list[dict],
) -> list[dict]:

    if not jobs:
        return []

    db = SessionLocal()

    try:
        sent_job_urls = (
            db.query(
                UserJob.job_url
            )
            .filter(
                UserJob.user_id == user.id
            )
            .all()
        )

        sent_urls = {
            row[0]
            for row in sent_job_urls
            if row[0]
        }

        return [
            job
            for job in jobs
            if (
                job.get("url")
                and job.get("url")
                not in sent_urls
            )
        ]

    except Exception as e:
        print(
            "[Notifier] Error checking sent jobs: "
            f"{e}"
        )

        # Fail closed.
        # If we cannot establish the sent state,
        # do not risk duplicate emails.
        return []

    finally:
        db.close()


def save_sent_jobs(
    user,
    jobs: list[dict],
):
    if not jobs:
        return

    db = SessionLocal()

    try:
        saved_count = 0

        for job in jobs:
            job_url = job.get(
                "url"
            )

            if not job_url:
                continue

            existing_job = (
                db.query(Job)
                .filter(
                    Job.url == job_url
                )
                .first()
            )

            if not existing_job:
                print(
                    "[Notifier] WARNING: "
                    f"Job {job_url} does not exist "
                    "in Job table"
                )
                continue

            already_linked = (
                db.query(UserJob)
                .filter(
                    UserJob.user_id == user.id,
                    UserJob.job_url == job_url,
                )
                .first()
            )

            if already_linked:
                continue

            db.add(
                UserJob(
                    user_id=user.id,
                    job_id=existing_job.id,
                    sent_at=datetime.utcnow(),
                    job_url=job_url,
                )
            )

            saved_count += 1

        db.commit()

        print(
            "[Notifier] Saved "
            f"{saved_count} sent jobs "
            f"for {user.email}"
        )

    except Exception as e:
        db.rollback()

        print(
            "[Notifier] Error saving sent jobs: "
            f"{e}"
        )

    finally:
        db.close()