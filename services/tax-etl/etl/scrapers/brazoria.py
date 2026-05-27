"""
Brazoria County — SE Houston / Gulf Coast.
Sources:
  - Brazoria CAD bulk export (APPRAISAL_INFO.TXT) — 194K properties (primary)
  - PBFCM tax sale PDF (auction metadata, kept as fallback)
"""
import logging
import os
import zipfile
import io
import re
from typing import List, Dict

import httpx
from etl.scrapers.pbfcm import ingest_county as pbfcm_ingest

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

BULK_PCLOUD_CODE = "kZMHpE5Znn3jRNFQAYb1Ys4uHiTxA4dFMJT7"
BULK_FILE_ID = "86778001624"
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "brazoria")
CACHE_ZIP = os.path.join(CACHE_DIR, "appraisal_export.zip")
CACHE_TXT = os.path.join(CACHE_DIR, "appraisal_info.txt")

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

DISTRESS_THRESHOLD = 1000
VALUE_CEILING = 50000

EXEMPT_OWNER_PREFIXES = [
    "USA-", "STATE-", "CITY-", "COUNTY", "TX-", "UNITED STATES",
    "BRAZORIA COUNTY", "BRAZORIA CITY", "SCHOOL DISTRICT",
    "INDEPENDENT SCHOOL", "ISD", "PORT OF", "NAVIGATION DISTRICT",
    "FLOOD CONTROL", "MUNICIPAL UTILITY", "DRAINAGE DISTRICT",
]


def _resolve_download_url() -> str:
    import requests as rq
    s = rq.Session()
    s.headers.update(HEADERS)
    resp = s.get(f"https://api.pcloud.com/getpublinkdownload?code={BULK_PCLOUD_CODE}&fileid={BULK_FILE_ID}")
    data = resp.json()
    if data.get("result") != 0:
        raise RuntimeError(f"pCloud API error: {data.get('error', 'unknown')}")
    return f"https://{data['hosts'][0]}{data['path']}"


def _ensure_cache():
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(CACHE_TXT):
        logging.info("[brazoria] using cached bulk data")
        return

    if not os.path.exists(CACHE_ZIP):
        dl_url = _resolve_download_url()
        logging.info(f"[brazoria] downloading bulk ZIP")
        resp = httpx.get(dl_url, headers=HEADERS, follow_redirects=True, timeout=600)
        with open(CACHE_ZIP, "wb") as f:
            f.write(resp.content)
        logging.info(f"[brazoria] cached {len(resp.content):,} bytes")

    logging.info("[brazoria] extracting TXT from ZIP")
    with zipfile.ZipFile(CACHE_ZIP) as zf:
        member = [n for n in zf.namelist() if n.endswith("_APPRAISAL_INFO.TXT")][0]
        with zf.open(member) as src, open(CACHE_TXT, "wb") as dst:
            dst.write(src.read())
    logging.info("[brazoria] cached TXT ready")


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
    records = []

    try:
        _ensure_cache()

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
                        "source": "brazoria_cad",
                        "county": "brazoria",
                        "is_delinquent": True,
                        "on_auction_list": False,
                    })

        logging.info(f"[brazoria/cad] total parcels: 194K | distress candidates: {len(records):,}")
    except Exception as e:
        logging.warning(f"[brazoria/cad] bulk download failed: {e}")

    # Fallback: add PBFCM PDF records if no bulk data
    if not records:
        records.extend(pbfcm_ingest("brazoria"))
        logging.info(f"[brazoria] fallback: {len(records)} from PBFCM PDF")

    return records
