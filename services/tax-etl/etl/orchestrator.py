"""
County ETL orchestrator. Routes to correct scraper, normalizer, and scorer.
"""
import logging
from etl.scrapers import harris, bell
from etl.normalizer import normalize_records
from etl.scorer import score_properties
from etl.db import upsert_properties, get_db
from etl.alerts import fire_tier_a_alerts

SCRAPER_MAP = {
    "harris": harris.ingest,
    "bell": bell.ingest,
}

def run_county_etl(county: str, dry_run: bool = False):
    scraper = SCRAPER_MAP.get(county)
    if not scraper:
        raise ValueError(f"No scraper registered for county: {county}")

    raw = scraper()
    logging.info(f"[{county}] raw records: {len(raw)}")

    normalized = normalize_records(raw, county)
    scored = score_properties(normalized)

    tier_a = [p for p in scored if p["distress_tier"] == "A"]
    logging.info(f"[{county}] Tier A: {len(tier_a)} | Tier B: {len([p for p in scored if p['distress_tier']=='B'])} | Total: {len(scored)}")

    if not dry_run:
        db = get_db()
        upsert_properties(db, scored)
        fire_tier_a_alerts(tier_a)
