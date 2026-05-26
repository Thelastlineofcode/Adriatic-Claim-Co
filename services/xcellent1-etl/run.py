#!/usr/bin/env python3
"""
Xcellent1 Lawn Care — LaPlace, LA Property ETL.
Primary: St. John the Baptist Parish.
Ring: St. Charles (west), St. James (east).

Usage:
  python run.py --parish st_john_the_baptist   # primary
  python run.py --parish all                   # full ring
  python run.py --parish st_john_the_baptist --dry-run
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
    parser = argparse.ArgumentParser(description="Xcellent1 ETL — LaPlace, LA")
    parser.add_argument(
        "--parish",
        choices=ALL_PARISHES + ["all"],
        default="st_john_the_baptist",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.parish == "all":
        run_all_etl(dry_run=args.dry_run)
    else:
        run_parish_etl(args.parish, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
