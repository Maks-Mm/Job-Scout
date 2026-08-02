#backend/app/workers/job_notifier.py

from app.collectors.collector_registry import get_collectors
from app.filters.job_filter import filter_jobs
from app.notifications.email_service import send_job_email


def check_new_jobs():

    print("[Notifier] checking jobs")


    users = get_users_with_alerts()


    for user in users:

        collectors = get_collectors(
            user.country
        )


        jobs=[]

        for collector in collectors:

            try:
                jobs.extend(
                    collector.fetch_jobs(user)
                )

            except Exception as e:
                print(
                    collector.source,
                    e
                )


        filtered = filter_jobs(
            jobs,
            user
        )


        new_jobs = remove_already_sent(
            user,
            filtered
        )


        if new_jobs:

            send_job_email(
                user.email,
                new_jobs
            )


            save_sent_jobs(
                user,
                new_jobs
            )



def get_users_with_alerts():
    """
    später Datenbank
    """
    return []



def remove_already_sent(user,jobs):
    return jobs


def save_sent_jobs(user,jobs):
    pass