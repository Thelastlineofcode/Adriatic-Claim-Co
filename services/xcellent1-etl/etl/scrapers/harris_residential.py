"""
Xcellent1 — Harris County residential distress scraper.

Filters HCAD + hctax + mvba for:
  - Single-family residential (property class R)
  - Appraised value < $250k (acquisition range)
  - Delinquent OR on auction list
  - Within Xcellent1 service ZIP codes

Reuses Harris data already ingested by tax-etl/harris.py.
This scraper adds the Xcellent1-specific filter layer + MLS comp enrichment.
"""
import logging
from typing import List, Dict
from etl.scrapers.mls_comps import enrich_with_comps
from etl.scrapers.code_enforcement import get_violations

logger = logging.getLogger(__name__)

# Xcellent1 primary service area ZIP codes (NW Houston + inner loop)
XCELLENT1_SERVICE_ZIPS = {
    "77040", "77041", "77055", "77080", "77092",  # NW Houston
    "77008", "77009", "77018", "77022",            # Heights / N Loop
    "77064", "77065", "77066", "77069",            # Spring Branch / Champions
    "77429", "77433",                              # Cypress
    "77084", "77094",                              # Katy / W Houston
}

MAX_VALUE = 250_000
RES_CLASSES = {"A1", "A2", "R1", "R2", "SFR"}  # HCAD residential property class codes


def ingest(candidates: List[Dict] = None) -> List[Dict]:
    """
    If candidates provided (from tax-etl harris ingest), filter them.
    Otherwise run harris ingest directly.
    """
    if candidates is None:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../tax-etl"))
        from etl.scrapers.harris import ingest as harris_ingest
        candidates = harris_ingest(use_bulk=True)

    filtered = []
    for r in candidates:
        val = float(str(r.get("appraised_value", 0)).replace(",", "") or 0)
        prop_class = r.get("property_class", "").upper()
        zip_code = r.get("zip", r.get("zip_code", "")).strip()
        in_service_zone = zip_code in XCELLENT1_SERVICE_ZIPS
        is_residential = any(c in prop_class for c in RES_CLASSES) or prop_class == ""
        is_distressed = r.get("is_delinquent") or r.get("on_auction_list")

        if is_distressed and is_residential and val <= MAX_VALUE:
            r["in_service_zone"] = in_service_zone
            r["acquisition_priority"] = "HIGH" if in_service_zone else "MEDIUM"
            filtered.append(r)

    logger.info(f"[xcellent1/harris] {len(filtered):,} residential distress candidates")

    # Enrich top candidates with MLS comps (Playwright)
    top = sorted(filtered, key=lambda x: x.get("appraised_value", 0))[:100]
    enriched = enrich_with_comps(top)
    for r in enriched:
        idx = next((i for i, c in enumerate(filtered) if c.get("parcel_id") == r.get("parcel_id")), None)
        if idx is not None:
            filtered[idx].update(r)

    return filtered
