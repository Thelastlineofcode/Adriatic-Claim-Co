"""
LGBS (Linebarger Goggan Blair & Sampson) REST API.
Provides auction-property overlay for all LGBS-served counties.
Covers Sale, Resale, Struck-off, and Future Sale properties.
"""
import logging
import httpx
from typing import List, Dict

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
API_BASE = "https://taxsales.lgbs.com/api/property_sales/"

COUNTIES = {
    "harris":     {"name": "HARRIS COUNTY",     "bbox": "-95.9605940907447,29.4966509198943,-94.90724921108219,30.1705872732631"},
    "montgomery": {"name": "MONTGOMERY COUNTY", "bbox": "-95.82998691246601,30.0262429992963,-95.0963969431644,30.630254917801896"},
    "brazoria":   {"name": "BRAZORIA COUNTY",   "bbox": "-95.8740231877199,28.828437850228397,-95.0558926842,29.598817641009802"},
    "chambers":   {"name": "CHAMBERS COUNTY",   "bbox": "-95.0012201774692,29.511703418867697,-94.3532412341956,29.8900967913175"},
    "galveston":  {"name": "GALVESTON COUNTY",  "bbox": "-95.2329024968527,29.086335989111898,-94.3705906007756,29.5981046054316"},
    "liberty":    {"name": "LIBERTY COUNTY",    "bbox": "-95.1655957888146,29.8850955031386,-94.44207792155879,30.4899138401255"},
    "fort_bend":  {"name": "FORT BEND COUNTY",  "bbox": "-96.08904305978929,29.2623579792315,-95.42378223056551,29.7883017150374"},
    "bell":       {"name": "BELL COUNTY",       "bbox": "-97.91333779790101,30.7521953996677,-97.06986172993489,31.3200131257661"},
}


def fetch_properties(county_name: str, bbox: str) -> List[Dict]:
    all_results = []
    offset = 0
    while True:
        url = f"{API_BASE}?county={county_name}&in_bbox={bbox}&state=TX&limit=100&offset={offset}&sale_type=SALE,RESALE,STRUCK+OFF,FUTURE+SALE&ordering=precinct,sale_nbr,uid"
        resp = httpx.get(url, headers=HEADERS, timeout=30)
        data = resp.json()
        all_results.extend(data["results"])
        if data["next"] is None:
            break
        offset += 100
    return all_results


def _lgbs_to_record(r: Dict) -> Dict:
    address = ", ".join(filter(None, [r.get("prop_address_one", ""), r.get("prop_city", ""), r.get("prop_state", ""), r.get("prop_zipcode", "")]))
    return {
        "parcel_id": r.get("account_nbr", ""),
        "owner_name": r.get("street_name", "").replace("VACANT LOTS ", "").replace("VACANT LOT ", "").strip(),
        "address": address,
        "appraised_value": float(r.get("value", 0) or 0),
        "min_bid": float(r.get("minimum_bid", 0) or 0),
        "est_tax_due": float(r.get("minimum_bid", 0) or 0),
        "cause_no": r.get("cause_nbr", ""),
        "sale_type": r.get("sale_type", ""),
        "status": r.get("status", ""),
        "sale_date": r.get("sale_date", ""),
        "source": "lgbs",
        "county": "",
        "is_delinquent": True,
        "on_auction_list": r.get("sale_type") in ("SALE", "RESALE"),
    }


def ingest_county(county_slug: str) -> List[Dict]:
    """Standalone LGBS ingestion for counties that have no other source."""
    cfg = COUNTIES.get(county_slug)
    if not cfg:
        logging.warning(f"[lgbs] unknown county: {county_slug}")
        return []
    try:
        rows = fetch_properties(cfg["name"], cfg["bbox"])
        records = [_lgbs_to_record(r) for r in rows]
        for rec in records:
            rec["county"] = county_slug
        logging.info(f"[lgbs/{county_slug}] {len(records)} records")
        return records
    except Exception as e:
        logging.warning(f"[lgbs/{county_slug}] failed: {e}")
        return []


def enrich(records: List[Dict], county_slug: str) -> List[Dict]:
    """Overlay LGBS auction data onto existing scraped records.

    For each LGBS property matching a parcel_id in the existing records,
    enrich with auction metadata (cause_no, sale_type, status, sale_date).
    LGBS properties with no match are appended as new records.
    """
    cfg = COUNTIES.get(county_slug)
    if not cfg:
        return records

    try:
        lgbs_rows = fetch_properties(cfg["name"], cfg["bbox"])
    except Exception as e:
        logging.warning(f"[lgbs/enrich/{county_slug}] fetch failed: {e}")
        return records

    if not lgbs_rows:
        logging.info(f"[lgbs/enrich/{county_slug}] no LGBS data to overlay")
        return records

    lookup = {}
    for i, r in enumerate(records):
        pid = r.get("parcel_id", "") or r.get("account_nbr", "")
        if pid:
            lookup[pid] = i

    matched = 0
    new_records = []
    for lr in lgbs_rows:
        lr_pid = lr.get("account_nbr", "")
        overlay = {
            "cause_no": lr.get("cause_nbr", ""),
            "sale_type": lr.get("sale_type", ""),
            "status": lr.get("status", ""),
            "sale_date": lr.get("sale_date", ""),
            "on_auction_list": lr.get("sale_type") in ("SALE", "RESALE"),
        }

        if lr_pid and lr_pid in lookup:
            idx = lookup[lr_pid]
            records[idx].update(overlay)
            matched += 1
        else:
            rec = _lgbs_to_record(lr)
            rec["county"] = county_slug
            new_records.append(rec)

    merged = records + new_records
    logging.info(f"[lgbs/enrich/{county_slug}] matched={matched} new={len(new_records)} lgbs_total={len(lgbs_rows)} merged={len(merged)}")
    return merged
