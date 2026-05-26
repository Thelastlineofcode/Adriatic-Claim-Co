#!/usr/bin/env python3
"""
Nightly scheduler — Gulf Coast sweep.
Harris runs nightly with HCAD bulk. Surrounding counties staggered.
Usage: python scripts/schedule.py
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import logging

logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")


def run(county: str):
    logging.info(f"Scheduled ETL: {county}")
    result = subprocess.run(["python", "run.py", "--county", county], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"[{county}] ETL error: {result.stderr[-500:]}")
    else:
        logging.info(f"[{county}] complete")


scheduler = BlockingScheduler(timezone="America/Chicago")

# Harris — nightly 1 AM (bulk download, primary)
scheduler.add_job(lambda: run("harris"),    CronTrigger(hour=1, minute=0))

# Gulf Coast ring — staggered to avoid hammering sources
scheduler.add_job(lambda: run("galveston"),  CronTrigger(hour=1, minute=30))
scheduler.add_job(lambda: run("fort_bend"),  CronTrigger(hour=2, minute=0))
scheduler.add_job(lambda: run("brazoria"),   CronTrigger(hour=2, minute=20))
scheduler.add_job(lambda: run("montgomery"), CronTrigger(hour=2, minute=40))
scheduler.add_job(lambda: run("chambers"),   CronTrigger(hour=3, minute=0))
scheduler.add_job(lambda: run("liberty"),    CronTrigger(hour=3, minute=15))
# Bell — Adrianne's Bramble Bush area
scheduler.add_job(lambda: run("bell"),       CronTrigger(hour=3, minute=30))

logging.info("""
Schedule (CDT):
  1:00 AM  Harris (primary, HCAD bulk)
  1:30 AM  Galveston
  2:00 AM  Fort Bend
  2:20 AM  Brazoria
  2:40 AM  Montgomery
  3:00 AM  Chambers
  3:15 AM  Liberty
  3:30 AM  Bell
""")
scheduler.start()
