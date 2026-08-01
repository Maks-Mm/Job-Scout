import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.collectors import get_collectors
from app.services.filtering import JobFilter


print("=" * 60)
print("TESTING AUSTRIA COLLECTORS")
print("=" * 60)

filters = JobFilter(
    country="Austria",
    city="Vienna",
    keywords="",
    language="de",
)

collectors = get_collectors("austria")
for collector in collectors:
    print(f"\nTesting {collector.source}...")
    try:
        jobs = collector.fetch_jobs(filters)
        print(f"  Found {len(jobs)} jobs")
        if jobs:
            print(f"  First job: {jobs[0].get('title', 'No title')}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("TESTING SWITZERLAND COLLECTORS")
print("=" * 60)

filters = JobFilter(
    country="Switzerland",
    city="Zurich",
    keywords="",
    language="de",
)

collectors = get_collectors("switzerland")
for collector in collectors:
    print(f"\nTesting {collector.source}...")
    try:
        jobs = collector.fetch_jobs(filters)
        print(f"  Found {len(jobs)} jobs")
        if jobs:
            print(f"  First job: {jobs[0].get('title', 'No title')}")
    except Exception as e:
        print(f"  ERROR: {e}")
