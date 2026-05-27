"""
County ETL orchestrator — Gulf Coast expansion from Harris outward.
Registered counties cover the full Houston / Gulf Coast metro area.

Every county gets an LGBS enrichment overlay after its primary scraper:
adds auction metadata (cause_no, sale_type, status, sale_date) for any
LGBS property matching a parcel_id, and appends unmatched LGBS properties.
"""
import logging
from etl.scrapers import harris, galveston, fort_bend, montgomery, brazoria, chambers, liberty, bell
from etl.scrapers.lgbs import enrich as lgbs_enrich
from etl.normalizer import normalize_records
from etl.scorer import score_properties
from etl.db import upsert_properties, get_db
from etl.alerts import fire_tier_a_alerts

# Expansion order: Harris first, then ring outward by geography
SCRAPER_MAP = {
    "harris":      harris.ingest,       # Primary — Houston, 1.6M+ parcels
    "galveston":   galveston.ingest,    # Gulf Coast / waterfront
    "fort_bend":   fort_bend.ingest,    # SW Houston growth
    "brazoria":    brazoria.ingest,     # SE / Gulf Coast
    "montgomery":  montgomery.ingest,  # North Houston
    "chambers":    chambers.ingest,    # East — low competition
    "liberty":     liberty.ingest,     # NE — rural, underserved
    "bell":        bell.ingest,        # Bell County (Adrianne's Bramble Bush target)
}

GULF_COAST_COUNTIES = ["harris", "galveston", "fort_bend", "brazoria", "montgomery", "chambers", "liberty"]
ALL_COUNTIES = list(SCRAPER_MAP.keys())


def run_county_etl(county: str, dry_run: bool = False):
    scraper = SCRAPER_MAP.get(county)
    if not scraper:
        raise ValueError(f"No scraper registered for county: {county}")

    raw = scraper()
    logging.info(f"[{county}] raw records: {len(raw):,}")

    raw = lgbs_enrich(raw, county)
    logging.info(f"[{county}] after lgbs enrichment: {len(raw):,}")

    normalized = normalize_records(raw, county)
    scored = score_properties(normalized)

    tier_a = [p for p in scored if p["distress_tier"] == "A"]
    tier_b = [p for p in scored if p["distress_tier"] == "B"]
    logging.info(f"[{county}] Tier A: {len(tier_a)} | Tier B: {len(tier_b)} | Total: {len(scored):,}")

    if not dry_run:
        db = get_db()
        upsert_properties(db, scored)
        fire_tier_a_alerts(tier_a)


def run_gulf_coast_etl(dry_run: bool = False):
    """Run full Gulf Coast sweep — all ring counties around Harris."""
    for county in GULF_COAST_COUNTIES:
        try:
            logging.info(f"=== Starting {county.upper()} ===")
            run_county_etl(county, dry_run=dry_run)
        except Exception as e:
            logging.error(f"[{county}] ETL failed: {e}", exc_info=True)
