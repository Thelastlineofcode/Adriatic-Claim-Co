#!/usr/bin/env python3
"""
Main ETL runner for Adriatic Claim Co — Tax Lien Pipeline.
Starts from Harris County (Gulf Coast anchor), expands outward.

Usage:
  python run.py --county harris           # single county
  python run.py --county gulf_coast       # all Gulf Coast counties
  python run.py --county all              # everything including Bell
  python run.py --county harris --dry-run # parse only, no DB write
"""
import argparse
import logging
from dotenv import load_dotenv
from etl.orchestrator import run_county_etl, run_gulf_coast_etl, ALL_COUNTIES

load_dotenv()
logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("./data/etl.log", mode="a"),
    ]
)


def main():
    parser = argparse.ArgumentParser(description="Adriatic Claim Co — Tax Lien ETL")
    parser.add_argument(
        "--county",
        choices=ALL_COUNTIES + ["gulf_coast", "all"],
        default="harris",
        help="County to run. 'gulf_coast' runs all Gulf Coast counties. 'all' includes Bell."
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse only, no DB write")
    args = parser.parse_args()

    if args.county == "gulf_coast":
        run_gulf_coast_etl(dry_run=args.dry_run)
    elif args.county == "all":
        for county in ALL_COUNTIES:
            try:
                run_county_etl(county, dry_run=args.dry_run)
            except Exception as e:
                logging.error(f"[{county}] failed: {e}")
    else:
        run_county_etl(args.county, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
