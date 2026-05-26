#!/usr/bin/env python3
"""
Nightly scheduler — runs ETL on a cron-like schedule.
Run this once to keep Z-34 refreshing data automatically.
Usage: python scripts/schedule.py
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import logging

logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")

def run_harris():
    logging.info("Scheduled ETL: harris county")
    subprocess.run(["python", "run.py", "--county", "harris"], check=True)

def run_bell():
    logging.info("Scheduled ETL: bell county")
    subprocess.run(["python", "run.py", "--county", "bell"], check=True)

scheduler = BlockingScheduler()
# Harris: every night at 2 AM
scheduler.add_job(run_harris, CronTrigger(hour=2, minute=0))
# Bell: every night at 2:30 AM
scheduler.add_job(run_bell, CronTrigger(hour=2, minute=30))

logging.info("Scheduler started. Harris @ 2:00 AM, Bell @ 2:30 AM nightly.")
scheduler.start()
