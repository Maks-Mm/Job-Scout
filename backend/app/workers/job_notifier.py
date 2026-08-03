# backend/app/workers/job_notifier.py

from app.collectors.collector_registry import get_collectors
from app.services.filtering import filter_jobs, JobFilter  # Korrekter Import
from app.notifications.email_service import send_job_email
from app.core.database import SessionLocal
from app.models.user import User
from app.models.job import Job
from app.models.user_job import UserJob
from datetime import datetime
from sqlalchemy import and_


def check_new_jobs():
    print("[Notifier] checking jobs")

    users = get_users_with_alerts()

    for user in users:
        collectors = get_collectors(user.country)

        jobs = []

        for collector in collectors:
            try:
                # Jobs von den Collectors holen
                jobs.extend(collector.fetch_jobs(user))
            except Exception as e:
                print(f"[Notifier] Collector {collector.source} error: {e}")

        # Jobs mit dem bestehenden JobFilter filtern
        filter_params = JobFilter(
            country=user.country,
            city=user.city,
            keywords=user.keywords,
            language=getattr(user, 'language', 'de'),
            min_salary=getattr(user, 'min_salary', None),
            max_salary=getattr(user, 'max_salary', None),
            # Weitere Filter nach Bedarf
        )
        
        filtered = filter_jobs(jobs, filter_params)

        # Bereits gesendete Jobs entfernen
        new_jobs = remove_already_sent(user, filtered)

        if new_jobs:
            print(f"[Notifier] Sending {len(new_jobs)} new jobs to {user.email}")
            send_job_email(user.email, new_jobs)

            # Gesendete Jobs speichern
            save_sent_jobs(user, new_jobs)


def get_users_with_alerts():
    """
    Alle Benutzer mit aktivierten Benachrichtigungen abrufen
    """
    db = SessionLocal()
    try:
        users = db.query(User).filter(
            User.alerts_enabled == True
        ).all()
        return users
    except Exception as e:
        print(f"[Notifier] Error fetching users: {e}")
        return []
    finally:
        db.close()


def remove_already_sent(user, jobs):
    """
    Jobs herausfiltern, die bereits an diesen Benutzer gesendet wurden
    """
    if not jobs:
        return []

    db = SessionLocal()
    try:
        # URLs der bereits gesendeten Jobs abrufen
        sent_job_urls = db.query(UserJob.job_url).filter(
            UserJob.user_id == user.id
        ).all()
        sent_urls = {url[0] for url in sent_job_urls}

        # Jobs filtern, die noch nicht gesendet wurden
        new_jobs = [job for job in jobs if job.get('url') not in sent_urls]
        return new_jobs
    except Exception as e:
        print(f"[Notifier] Error checking sent jobs: {e}")
        return jobs
    finally:
        db.close()


def save_sent_jobs(user, jobs):
    """
    Gesendete Jobs speichern, um Duplikate zu vermeiden
    """
    if not jobs:
        return

    db = SessionLocal()
    try:
        for job in jobs:
            # Prüfen, ob dieser Job bereits in der Datenbank existiert
            existing_job = db.query(Job).filter(
                Job.url == job.get('url')
            ).first()

            if not existing_job:
                # Neuen Job erstellen, falls er nicht existiert
                existing_job = Job(
                    title=job.get('title'),
                    company=job.get('company'),
                    city=job.get('city'),
                    salary_min=job.get('salary_min'),
                    salary_max=job.get('salary_max'),
                    currency=job.get('currency', 'EUR'),
                    url=job.get('url'),
                    source=job.get('source'),
                    date=job.get('date', datetime.now().isoformat())
                )
                db.add(existing_job)
                db.flush()  # ID erhalten

            # UserJob-Eintrag erstellen, um zu tracken, dass dieser Job an diesen Benutzer gesendet wurde
            user_job = UserJob(
                user_id=user.id,
                job_id=existing_job.id,
                sent_at=datetime.now(),
                job_url=job.get('url')
            )
            db.add(user_job)

        db.commit()
        print(f"[Notifier] Saved {len(jobs)} sent jobs for user {user.id}")
    except Exception as e:
        db.rollback()
        print(f"[Notifier] Error saving sent jobs: {e}")
    finally:
        db.close()