"""
Normalizes raw scraped records into a consistent schema.
Handles currency strings, address casing, missing fields.
"""
import re
from typing import List, Dict

def parse_currency(val) -> float:
    if val is None:
        return 0.0
    return float(re.sub(r"[^\d.]", "", str(val)) or 0)

def normalize_address(addr: str) -> str:
    if not addr:
        return ""
    return " ".join(addr.upper().split())

def normalize_records(raw: List[Dict], county: str) -> List[Dict]:
    out = []
    for r in raw:
        out.append({
            "parcel_id": str(r.get("parcel_id") or "").strip(),
            "owner_name": str(r.get("owner_name") or "").strip().upper(),
            "address": normalize_address(r.get("address") or ""),
            "city": str(r.get("city") or "").strip().upper(),
            "county": county,
            "appraised_value": parse_currency(r.get("appraised_value")),
            "est_tax_due": parse_currency(r.get("est_tax_due")),
            "min_bid": parse_currency(r.get("min_bid")),
            "is_delinquent": bool(r.get("is_delinquent", False)),
            "on_auction_list": bool(r.get("on_auction_list", False)),
            "auction_date": r.get("auction_date"),
            "source": r.get("source", "unknown"),
            "is_flood_zone": r.get("is_flood_zone"),  # None = unchecked
            "flood_zone_code": r.get("flood_zone_code"),
        })
    return out
