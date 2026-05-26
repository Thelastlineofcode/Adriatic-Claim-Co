#!/usr/bin/env python3
"""
Main ETL runner. Called nightly via cron or manually.
Usage: python run.py --county harris
"""
import argparse
import logging
from dotenv import load_dotenv
from etl.orchestrator import run_county_etl

load_dotenv()
logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")

COUNTY_ORDER = ["harris", "bell", "fort_bend", "galveston", "montgomery"]

def main():
    parser = argparse.ArgumentParser(description="Adriatic Tax Lien ETL")
    parser.add_argument("--county", choices=COUNTY_ORDER + ["all"], default="harris")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, no DB write")
    args = parser.parse_args()

    counties = COUNTY_ORDER if args.county == "all" else [args.county]
    for county in counties:
        logging.info(f"Starting ETL for {county} county...")
        run_county_etl(county, dry_run=args.dry_run)
        logging.info(f"Completed ETL for {county} county")

if __name__ == "__main__":
    main()
