#!/usr/bin/env python3
"""
Grandee's Property ETL — St. Charles Parish, Louisiana.

Usage:
  python run.py --parish st_charles
  python run.py --parish all
  python run.py --parish st_charles --dry-run
"""
import argparse
import logging
from dotenv import load_dotenv
from etl.orchestrator import run_parish_etl, run_all_etl, ALL_PARISHES

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
    parser = argparse.ArgumentParser(description="Grandee's ETL — St. Charles Parish")
    parser.add_argument(
        "--parish",
        choices=ALL_PARISHES + ["all"],
        default="st_charles",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.parish == "all":
        run_all_etl(dry_run=args.dry_run)
    else:
        run_parish_etl(args.parish, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
