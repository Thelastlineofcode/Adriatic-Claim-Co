#!/usr/bin/env python3
"""
Grandee's nightly scheduler — St. Charles Parish ring, 4–5 AM CDT window.
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import logging

logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")


def run(parish: str):
    logging.info(f"Scheduled: {parish}")
    result = subprocess.run(["python", "run.py", "--parish", parish], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"[{parish}] error: {result.stderr[-400:]}")


scheduler = BlockingScheduler(timezone="America/Chicago")
scheduler.add_job(lambda: run("st_charles"),          CronTrigger(hour=4, minute=0))
scheduler.add_job(lambda: run("jefferson"),           CronTrigger(hour=4, minute=30))
scheduler.add_job(lambda: run("st_john_the_baptist"), CronTrigger(hour=5, minute=0))

logging.info("""
Grandee's Schedule (CDT):
  4:00 AM  St. Charles (primary)
  4:30 AM  Jefferson
  5:00 AM  St. John the Baptist
""")
scheduler.start()
