from sqlalchemy.orm import Session

from app.models.job import Job

from app.collectors.adzuna import fetch_jobs



def collect_jobs(
        city:str,
        db:Session
):

    jobs = fetch_jobs(city)


    for item in jobs:


        exists = db.query(Job).filter(
            Job.url == item["url"]
        ).first()


        if exists:
            continue


        job = Job(**item)

        db.add(job)



    db.commit()



    return db.query(Job).all()