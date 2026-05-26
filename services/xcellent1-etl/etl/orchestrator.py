"""
Xcellent1 ETL orchestrator — Houston metro residential distress.
"""
import logging
from etl.scrapers import harris_residential

SCRAPER_MAP = {
    "harris_nw":  harris_residential.ingest,
    "harris_all": harris_residential.ingest,
}

ZONES = list(SCRAPER_MAP.keys())


def run_zone_etl(zone: str, dry_run: bool = False):
    scraper = SCRAPER_MAP.get(zone)
    if not scraper:
        raise ValueError(f"No scraper for zone: {zone}")
    raw = scraper()
    logging.info(f"[xcellent1/{zone}] {len(raw):,} candidates")
    if not dry_run:
        from etl.db import upsert_properties, get_db
        db = get_db()
        upsert_properties(db, raw)


def run_all_etl(dry_run: bool = False):
    for zone in ZONES:
        try:
            run_zone_etl(zone, dry_run=dry_run)
        except Exception as e:
            logging.error(f"[xcellent1/{zone}] failed: {e}", exc_info=True)
