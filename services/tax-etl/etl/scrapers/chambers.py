"""
Chambers County — East of Harris.
Sources:
  - Chambers CAD certified roll CSV (primary, 43K parcels)
  - PBFCM tax sale PDF (auction metadata, keeps as fallback)
"""
import csv
import io
import re
import logging
from pathlib import Path
from typing import Dict, List

import httpx
import requests
from pypdf import PdfReader

CACHE_DIR = Path(".cache") / "chambers"
CACHE_CSV = CACHE_DIR / "chambers_roll.csv"
CSV_URL = "https://chamberscad.org/Forms/ExcelDownload"
CSV_PARAMS = {
    "subPath": "Data Records",
    "fileName": "1775481735_2026 Chambers Co Appraisal District Preliminary Appraisal Roll-Excel_2026.03.30.csv",
}
PDF_URL = "https://www.pbfcm.com/docs/taxdocs/sales/06-2026chamberstaxsale.pdf"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

DISTRESS_THRESHOLD = 50000

EXEMPT_OWNER_PREFIXES = [
    "USA-", "STATE-", "CITY-", "COUNTY", "TX-", "UNITED STATES",
    "CHAMBERS COUNTY", "SCHOOL DISTRICT",
    "INDEPENDENT SCHOOL", "ISD", "PORT OF", "NAVIGATION DISTRICT",
    "FLOOD CONTROL", "MUNICIPAL UTILITY", "DRAINAGE DISTRICT",
]


def _ensure_cache():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not CACHE_CSV.exists():
        logging.info("[chambers] downloading CSV from Chambers CAD")
        s = requests.Session()
        s.headers.update(HEADERS)
        s.get("https://chamberscad.org/home/DataRecords")
        resp = s.get(CSV_URL, params=CSV_PARAMS)
        resp.raise_for_status()
        CACHE_CSV.write_bytes(resp.content)
        logging.info(f"[chambers] cached {len(resp.content):,} bytes")
    else:
        logging.info("[chambers] using cached CSV")


def _parse_value(val: str) -> float:
    try:
        return float(val.replace(",", "").strip()) if val.strip() else 0.0
    except (ValueError, AttributeError):
        return 0.0


def is_distressed(rec: Dict) -> bool:
    name = (rec.get("owner_name", "") or "").upper().strip()
    for prefix in EXEMPT_OWNER_PREFIXES:
        if name.startswith(prefix) or prefix in name:
            return False
    if rec.get("is_exempt", "").upper() in ("Y", "YES", "1"):
        return False

    val = rec.get("appraised_value", 0)
    if val <= 0 or val > 10000000:
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


def ingest_csv() -> List[Dict]:
    _ensure_cache()
    records = []

    with open(CACHE_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("Name", "") or "").strip()
            if not name:
                continue

            val = _parse_value(row.get("Market_Value", "0"))
            rec = {
                "parcel_id": (row.get("Parcel_ID", "") or "").strip(),
                "owner_name": name,
                "address": f"{row.get('Street', '')}, {row.get('City', '')}, {row.get('State', '')} {row.get('Zip5', '')}".strip().strip(","),
                "appraised_value": val,
                "market_value": val,
                "is_exempt": (row.get("Is_Exempt", "") or "").strip(),
                "source": "chambers_cad_csv",
                "county": "chambers",
            }
            if is_distressed(rec):
                records.append(rec)

    logging.info(f"[chambers/csv] {len(records)} distress candidates from {CACHE_CSV}")
    return records


def parse_chambers_pdf(content: bytes) -> List[Dict]:
    """Parse Chambers County PBFCM PDF — table format with cause-number-delimited records."""
    reader = PdfReader(io.BytesIO(content))
    full_text = "\n".join(page.extract_text() for page in reader.pages)
    lines = [l.strip() for l in full_text.split("\n") if l.strip()]

    cause_idx = [i for i, l in enumerate(lines) if re.search(r"\b\d{2}DCV\d{4}\b", l)]
    records = []

    for idx in range(len(cause_idx)):
        start = cause_idx[idx]
        end = cause_idx[idx + 1] if idx + 1 < len(cause_idx) else len(lines)
        block = lines[start:end]
        text = " ".join(block)
        cause_match = re.search(r"(\d{2}DCV\d{4})", text)
        cause_no = cause_match.group(1) if cause_match else ""
        vs_match = re.search(r"vs\.\s+(.+?)(?=\s+(?:BEING|A TRACT|A \d|LOT|ALL THAT|ACRE|$[\d,]+\.\d{2}))", text, re.IGNORECASE)
        if not vs_match:
            vs_match = re.search(r"vs\.\s+(.+?)(?:\.|\s{4,})(?:\s|$)", text, re.IGNORECASE)
        owner = ""
        if vs_match:
            owner = re.sub(r"\s+", " ", vs_match.group(1)).strip().strip(",")
            owner = re.sub(r",\s*ET\s+AL.*$", "", owner, flags=re.IGNORECASE).strip()
        amounts = re.findall(r"\$([\d,]+\.\d{2})", text)
        if not amounts:
            amounts = re.findall(r"(?<!\d)([\d,]+\.\d{2})(?!(?:\s*(?:ACRE|ACRES|TRACT)))", text)
            amounts = [a for a in amounts if float(a.replace(",", "")) > 100]
        appraised_value = 0
        min_bid = 0
        if len(amounts) >= 2:
            vals = sorted([float(a.replace(",", "")) for a in amounts], reverse=True)
            appraised_value = vals[0]
            min_bid = vals[-1]
        elif len(amounts) == 1:
            appraised_value = float(amounts[0].replace(",", ""))
            min_bid = appraised_value
        cad_match = re.search(r"(\d{5}-\d{5}-\d{5}-\d{6})", text)
        if cad_match:
            parcel_id = cad_match.group(1)
        else:
            geo_match = re.search(r"GEO:\s*(\S+)", text, re.IGNORECASE)
            parcel_id = geo_match.group(1).strip().strip(",") if geo_match else ""
        records.append({
            "parcel_id": parcel_id,
            "owner_name": owner,
            "address": "",
            "appraised_value": appraised_value,
            "min_bid": min_bid,
            "cause_no": cause_no,
            "source": "pbfcm_chambers",
            "county": "chambers",
            "is_delinquent": True,
            "on_auction_list": True,
        })
    return records


def ingest_pdf() -> List[Dict]:
    records = []
    try:
        content = httpx.get(PDF_URL, headers=HEADERS, follow_redirects=True, timeout=30, verify=False).content
        records = parse_chambers_pdf(content)
        logging.info(f"[chambers/pbfcm] {len(records)} records")
    except Exception as e:
        logging.warning(f"[chambers/pbfcm] failed: {e}")
    seen = {}
    for r in records:
        pid = r.get("parcel_id") or r.get("cause_no", "")
        if pid and pid not in seen:
            seen[pid] = r
    return list(seen.values())


def ingest() -> List[Dict]:
    csv_records = ingest_csv()
    logging.info(f"[chambers] CSV distress: {len(csv_records)}")
    return csv_records
