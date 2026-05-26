"""
Grandee's ETL orchestrator — St. Charles Parish anchor, LA ring outward.
"""
import logging
from etl.scrapers import st_charles, jefferson, st_john_the_baptist

SCRAPER_MAP = {
    "st_charles":          st_charles.ingest,
    "jefferson":           jefferson.ingest,
    "st_john_the_baptist": st_john_the_baptist.ingest,
}

LA_RING_PARISHES = ["st_charles", "jefferson", "st_john_the_baptist"]
ALL_PARISHES = list(SCRAPER_MAP.keys())


def run_parish_etl(parish: str, dry_run: bool = False):
    scraper = SCRAPER_MAP.get(parish)
    if not scraper:
        raise ValueError(f"No scraper registered for parish: {parish}")
    raw = scraper()
    logging.info(f"[{parish}] candidates: {len(raw):,}")
    if not dry_run:
        from etl.db import upsert_properties, get_db
        db = get_db()
        upsert_properties(db, raw)


def run_all_etl(dry_run: bool = False):
    for parish in ALL_PARISHES:
        try:
            logging.info(f"=== {parish.upper()} ===")
            run_parish_etl(parish, dry_run=dry_run)
        except Exception as e:
            logging.error(f"[{parish}] ETL failed: {e}", exc_info=True)
