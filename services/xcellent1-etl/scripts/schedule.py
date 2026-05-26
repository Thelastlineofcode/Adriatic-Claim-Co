#!/usr/bin/env python3
"""
Xcellent1 nightly scheduler — runs after tax-etl Harris (which finishes ~1:15 AM).
Harris residential filter runs at 5:30 AM to avoid contention with tax-etl.
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import logging

logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")


def run(zone: str):
    logging.info(f"Scheduled: xcellent1/{zone}")
    result = subprocess.run(["python", "run.py", "--zone", zone], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"[{zone}] error: {result.stderr[-400:]}")


scheduler = BlockingScheduler(timezone="America/Chicago")
scheduler.add_job(lambda: run("harris_all"), CronTrigger(hour=5, minute=30))

logging.info("""
Xcellent1 Schedule (CDT):
  5:30 AM  Harris residential filter + MLS comp enrichment
           (runs AFTER tax-etl Harris bulk download at 1 AM)
""")
scheduler.start()
