"""
Galveston County — Gulf Coast waterfront.
Sources:
  - Galveston CAD bulk export (APPRAISAL_INFO.TXT) — 211K properties
  - LGBS REST API overlay adds auction metadata via orchestrator
"""
import logging
import httpx
import os
import zipfile
import io
import re
from typing import List, Dict

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

BULK_URL = "https://galvestoncad.org/wp-content/uploads/2026/05/2025_as_of_Supp9_APPRAISAL_w_Owner_Exp3352.zip"
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "galveston")
CACHE_ZIP = os.path.join(CACHE_DIR, "appraisal_export.zip")
CACHE_TXT = os.path.join(CACHE_DIR, "appraisal_info.txt")

# Fixed-width field positions in APPRAISAL_INFO.TXT (9660 chars per record)
FIELDS = {
    "parcel_id":    (546, 565),
    "owner_code":   (596, 608),
    "owner_name":   (608, 680),
    "addr_street":  (753, 873),
    "addr_city":    (873, 923),
    "addr_state":   (923, 928),
    "addr_zip":     (978, 988),
    "val_raw":      (1659, 1675),
    "val_market":   (2771, 2803),
}

DISTRESS_THRESHOLD = 1000  # val_raw < 1000 (= ~$100K estimated market value)
VALUE_CEILING = 50000     # val_raw > 50000 (= ~$5M+) — too large for tax-sale distress

EXEMPT_OWNER_PREFIXES = [
    "USA-", "STATE-", "CITY-", "COUNTY", "TX-", "UNITED STATES",
    "GALVESTON COUNTY", "GALVESTON CITY", "SCHOOL DISTRICT",
    "INDEPENDENT SCHOOL", "ISD", "PORT OF", "NAVIGATION DISTRICT",
    "FLOOD CONTROL", "MUNICIPAL UTILITY", "DRAINAGE DISTRICT",
]


def _ensure_cache():
    """Download and cache the bulk ZIP, extract the main TXT."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(CACHE_TXT):
        logging.info("[galveston] using cached bulk data")
        return

    if not os.path.exists(CACHE_ZIP):
        logging.info(f"[galveston] downloading bulk ZIP ({BULK_URL})")
        resp = httpx.get(BULK_URL, headers=HEADERS, follow_redirects=True, timeout=600)
        with open(CACHE_ZIP, "wb") as f:
            f.write(resp.content)
        logging.info(f"[galveston] cached {len(resp.content):,} bytes")

    logging.info("[galveston] extracting TXT from ZIP")
    with zipfile.ZipFile(CACHE_ZIP) as zf:
        member = [n for n in zf.namelist() if n.endswith("_APPRAISAL_INFO.TXT")][0]
        with zf.open(member) as src, open(CACHE_TXT, "wb") as dst:
            dst.write(src.read())
    logging.info("[galveston] cached TXT ready")


def parse_record(line: str) -> Dict:
    r = {}
    for k, (start, end) in FIELDS.items():
        if end <= len(line):
            r[k] = line[start:end].strip()
        else:
            r[k] = ""
    r["val_raw"] = int(r.get("val_raw", "0") or "0")
    return r


def is_distressed(rec: Dict) -> bool:
    """Flag properties likely in tax distress."""
    val = rec.get("val_raw", 0)
    if val <= 0 or val > VALUE_CEILING:
        return False

    name = (rec.get("owner_name", "") or "").upper().strip()
    for prefix in EXEMPT_OWNER_PREFIXES:
        if name.startswith(prefix) or prefix in name:
            return False

    if val < DISTRESS_THRESHOLD:
        return True

    name_indicators = [
        "LLC", "LTD", "LP ", "INC", "TRUST", "TRUSTEE", "BANK", "ESTATE",
        "PROPERT", "HOLDING", "INVESTMENT", "MANAGEMENT",
    ]
    if any(ind in name for ind in name_indicators):
        return True

    state = (rec.get("addr_state", "") or "").upper()
    if state and state not in ("TX", ""):
        return True

    return False


def ingest() -> List[Dict]:
    _ensure_cache()

    records = []
    with open(CACHE_TXT, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or len(line) < 9000:
                continue
            rec = parse_record(line)
            if rec["parcel_id"] and is_distressed(rec):
                addr = ", ".join(filter(None, [rec.get("addr_street", ""), rec.get("addr_city", ""), rec.get("addr_state", ""), rec.get("addr_zip", "")]))
                records.append({
                    "parcel_id": rec["parcel_id"],
                    "owner_name": rec.get("owner_name", ""),
                    "address": addr,
                    "appraised_value": rec["val_raw"] * 100,
                    "min_bid": 0,
                    "est_tax_due": 0,
                    "source": "galveston_cad",
                    "county": "galveston",
                    "is_delinquent": True,
                    "on_auction_list": False,
                })

    logging.info(f"[galveston] total parcels: 211K | distress candidates: {len(records):,}")
    return records
