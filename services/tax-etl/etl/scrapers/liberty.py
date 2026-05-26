"""Liberty County — LGBS REST API (110 properties)."""
import logging
from typing import List, Dict
from etl.scrapers.lgbs import ingest_county

def ingest() -> List[Dict]:
    records = ingest_county("liberty")
    seen = {}
    for r in records:
        pid = r.get("parcel_id") or r.get("cause_no", "")
        if pid and pid not in seen:
            seen[pid] = r
    return list(seen.values())
