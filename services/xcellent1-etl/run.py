#!/usr/bin/env python3
"""
Xcellent1 Lawn Care — Houston Residential Property ETL.

Usage:
  python run.py --zone harris_nw
  python run.py --zone all
  python run.py --zone harris_nw --dry-run
"""
import argparse
import logging
from dotenv import load_dotenv
from etl.orchestrator import run_zone_etl, run_all_etl, ZONES

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
    parser = argparse.ArgumentParser(description="Xcellent1 ETL — Houston Residential")
    parser.add_argument("--zone", choices=ZONES + ["all"], default="harris_nw")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.zone == "all":
        run_all_etl(dry_run=args.dry_run)
    else:
        run_zone_etl(args.zone, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
