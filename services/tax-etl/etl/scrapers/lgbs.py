"""
LGBS (Linebarger Goggan Blair & Sampson) REST API scraper.
Covers: Galveston (211), Liberty (110), Fort Bend (23), and any LGBS-served county.
"""
import logging
import httpx
from typing import List, Dict

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
API_BASE = "https://taxsales.lgbs.com/api/property_sales/"

COUNTIES = {
    "galveston":  {"name": "GALVESTON COUNTY",  "bbox": "-95.2329024968527,29.086335989111898,-94.3705906007756,29.5981046054316"},
    "liberty":    {"name": "LIBERTY COUNTY",    "bbox": "-95.3739003154115,29.9584946229209,-94.4051458529853,30.4549414755281"},
    "fort_bend":  {"name": "FORT BEND COUNTY",  "bbox": "-96.08904305978929,29.2623579792315,-95.42378223056551,29.7883017150374"},
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


def ingest_county(county_slug: str) -> List[Dict]:
    cfg = COUNTIES.get(county_slug)
    if not cfg:
        logging.warning(f"[lgbs] unknown county: {county_slug}")
        return []
    try:
        rows = fetch_properties(cfg["name"], cfg["bbox"])
        records = []
        for r in rows:
            address = ", ".join(filter(None, [r.get("prop_address_one", ""), r.get("prop_city", ""), r.get("prop_state", ""), r.get("prop_zipcode", "")]))
            records.append({
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
                "county": county_slug,
                "is_delinquent": True,
                "on_auction_list": r.get("sale_type") in ("SALE", "RESALE"),
            })
        logging.info(f"[lgbs/{county_slug}] {len(records)} records")
        return records
    except Exception as e:
        logging.warning(f"[lgbs/{county_slug}] failed: {e}")
        return []
