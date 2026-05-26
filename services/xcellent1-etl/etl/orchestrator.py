"""
Xcellent1 ETL orchestrator — LaPlace, LA (St. John the Baptist Parish) anchor.
Ring parishes: St. Charles (west), St. James (east).
"""
import logging
from etl.scrapers import st_john_the_baptist, st_charles_ring, st_james

SCRAPER_MAP = {
    "st_john_the_baptist": st_john_the_baptist.ingest,   # PRIMARY — LaPlace
    "st_charles":          st_charles_ring.ingest,       # ring west
    "st_james":            st_james.ingest,              # ring east
}

LA_RING_PARISHES = ["st_john_the_baptist", "st_charles", "st_james"]
ALL_PARISHES = list(SCRAPER_MAP.keys())


def run_parish_etl(parish: str, dry_run: bool = False):
    scraper = SCRAPER_MAP.get(parish)
    if not scraper:
        raise ValueError(f"No scraper registered for parish: {parish}")
    raw = scraper()
    logging.info(f"[xcellent1/{parish}] candidates: {len(raw):,}")
    if not dry_run:
        from etl.db import upsert_properties, get_db
        db = get_db()
        upsert_properties(db, raw)


def run_all_etl(dry_run: bool = False):
    for parish in ALL_PARISHES:
        try:
            logging.info(f"=== XCELLENT1 | {parish.upper()} ===")
            run_parish_etl(parish, dry_run=dry_run)
        except Exception as e:
            logging.error(f"[xcellent1/{parish}] failed: {e}", exc_info=True)
