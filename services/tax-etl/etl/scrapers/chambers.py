"""
Chambers County — East of Harris, lower competition.
Sources:
  - PBFCM tax sale PDF (primary, confirmed working with 8 properties)
"""
import re
import logging
import httpx
import io
from typing import List, Dict
from pypdf import PdfReader

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


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

        vs_match = re.search(r"vs\.\s+(.+?)(?=\s+(?:BEING|A TRACT|A \d|LOT|ALL THAT|ACRE))", text, re.IGNORECASE)
        if not vs_match:
            vs_match = re.search(r"vs\.\s+(.+?)(?=\s+\$[\d,]+\.\d{2})", text, re.IGNORECASE)
        if not vs_match:
            vs_match = re.search(r"vs\.\s+(.+?)(?=\s+(?:A TRACT|AN UNDIVIDED|A CERTAIN))", text, re.IGNORECASE)
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
            if geo_match:
                parcel_id = geo_match.group(1).strip().strip(",")
            else:
                pn_match = re.search(r"PARCEL NUMBER\s*(\d+)", text, re.IGNORECASE)
                parcel_id = pn_match.group(1) if pn_match else ""

        prop_id_match = re.findall(r"\b\d{4,6}\b", text)
        property_id = prop_id_match[-1] if prop_id_match else ""

        records.append({
            "parcel_id": parcel_id,
            "property_id": property_id,
            "owner_name": owner,
            "address": "",
            "appraised_value": appraised_value,
            "min_bid": min_bid,
            "est_tax_due": min_bid,
            "cause_no": cause_no,
            "source": "pbfcm_chambers",
            "county": "chambers",
            "is_delinquent": True,
            "on_auction_list": True,
        })

    return records


def ingest() -> List[Dict]:
    records = []
    url = "https://www.pbfcm.com/docs/taxdocs/sales/06-2026chamberstaxsale.pdf"
    try:
        content = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=30, verify=False).content
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
