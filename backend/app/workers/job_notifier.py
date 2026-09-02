# backend/app/workers/job_notifier.py

from datetime import datetime

from app.services.filtering import filter_jobs, JobFilter
from app.notifications.email_service import send_job_email
from app.core.database import SessionLocal
from app.models.user import User
from app.models.job import Job
from app.models.user_job import UserJob


def check_new_jobs(new_jobs: list[dict]):
    print(
        f"[Notifier] Checking "
        f"{len(new_jobs)} newly discovered jobs"
    )

    if not new_jobs:
        print("[Notifier] No new jobs")
        return

    users = get_users_with_alerts()

    print(
        f"[Notifier] Found "
        f"{len(users)} eligible users"
    )

    if not users:
        print("[Notifier] No eligible users")
        return

    for user in users:
        process_user(user, new_jobs)


def process_user(user, new_jobs: list[dict]):
    print(
        f"[Notifier] Processing {user.email} "
        f"city={user.city} "
        f"keywords={user.keywords} "
        f"employment_type={user.employment_type} "
        f"salary={user.min_salary}-{user.max_salary}"
    )

    try:
        filter_params = JobFilter(
            country=getattr(user, "country", "Germany") or "Germany",
            city=getattr(user, "city", "") or "",
            keywords=getattr(user, "keywords", "") or "",
            language=getattr(user, "language", "de") or "de",
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
            f"[Notifier] Filter: "
            f"{filter_params.model_dump()}"
        )

        filtered = filter_jobs(
            new_jobs,
            filter_params,
        )

        print(
            f"[Notifier] Matching new jobs: "
            f"{len(filtered)}"
        )

        if not filtered:
            print(
                f"[Notifier] No matching jobs "
                f"for {user.email}"
            )
            return

        unsent = remove_already_sent(
            user,
            filtered,
        )

        print(
            f"[Notifier] Unsent jobs: "
            f"{len(unsent)}"
        )

        if not unsent:
            print(
                f"[Notifier] All matching jobs "
                f"already sent to {user.email}"
            )
            return

        unsent = _sort_by_freshness(unsent)

        print(
            f"[Notifier] Sending "
            f"{len(unsent)} jobs to {user.email}"
        )

        sent = send_job_email(
            receiver=user.email,
            jobs=unsent,
            unsubscribe_token=user.unsubscribe_token,
            user_filters={
                "city": getattr(user, "city", ""),
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
            f"[Notifier] send_job_email result: {sent}"
        )

        if sent is True:
            save_sent_jobs(user, unsent)

        else:
            print(
                f"[Notifier] Email failed for "
                f"{user.email}; "
                f"jobs remain unsent"
            )

    except Exception as e:
        print(
            f"[Notifier] Error processing "
            f"{user.email}: {e}"
        )


def _sort_by_freshness(
    jobs: list[dict],
) -> list[dict]:
    def _date_key(job: dict):
        raw = (
            job.get("date")
            or job.get("created_at")
            or job.get("posted_at")
            or ""
        )

        if not raw:
            return ""

        return raw[:10]

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
            f"[Notifier] Error fetching users: {e}"
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
            db.query(UserJob.job_url)
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
            if job.get("url")
            and job.get("url") not in sent_urls
        ]

    except Exception as e:
        print(
            f"[Notifier] Error checking sent jobs: {e}"
        )
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
            job_url = job.get("url")

            if not job_url:
                continue

            existing_job = (
                db.query(Job)
                .filter(Job.url == job_url)
                .first()
            )

            if not existing_job:
                print(
                    f"[Notifier] WARNING: "
                    f"Job {job_url} does not exist "
                    f"in Job table"
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
            f"[Notifier] Saved "
            f"{saved_count} sent jobs "
            f"for {user.email}"
        )

    except Exception as e:
        db.rollback()

        print(
            f"[Notifier] Error saving sent jobs: {e}"
        )

    finally:
        db.close()