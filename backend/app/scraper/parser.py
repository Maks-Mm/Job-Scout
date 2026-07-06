#backend/app/scraper/parser.py

from bs4 import BeautifulSoup


def parse_job_cards(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    jobs=[]


    for item in soup.select(
        ".job-card"
    ):

        jobs.append({

            "title":
                item.text.strip(),

        })


    return jobs