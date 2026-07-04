#backend/app/workers/scheduler.py


from apscheduler.schedulers.background import BackgroundScheduler

from app.services.job_service import get_jobs


scheduler = BackgroundScheduler()


def update_jobs():

    cities=[

        "Munich",
        "Berlin",
        "Hamburg"

    ]


    for city in cities:

        jobs=get_jobs(city)


        print(
            city,
            len(jobs),
            "jobs collected"
        )


def start_scheduler():

    scheduler.add_job(
        update_jobs,
        "interval",
        hours=6
    )


    scheduler.start()