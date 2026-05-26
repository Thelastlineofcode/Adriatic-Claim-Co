#!/usr/bin/env python3
"""
Xcellent1 nightly scheduler — LaPlace, LA ring.
Staggered in the 5–6 AM CDT window, after Grandee's completes at 5 AM.
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import logging

logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")


def run(parish: str):
    logging.info(f"Scheduled: xcellent1/{parish}")
    result = subprocess.run(["python", "run.py", "--parish", parish], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"[{parish}] error: {result.stderr[-400:]}")


scheduler = BlockingScheduler(timezone="America/Chicago")
scheduler.add_job(lambda: run("st_john_the_baptist"), CronTrigger(hour=5, minute=30))
scheduler.add_job(lambda: run("st_charles"),          CronTrigger(hour=5, minute=50))
scheduler.add_job(lambda: run("st_james"),            CronTrigger(hour=6, minute=10))

logging.info("""
Xcellent1 Schedule (CDT):
  5:30 AM  St. John the Baptist (PRIMARY — LaPlace)
  5:50 AM  St. Charles (ring west)
  6:10 AM  St. James (ring east)
""")
scheduler.start()
