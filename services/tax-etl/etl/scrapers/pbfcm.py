"""
PBFCM (Perdue, Brandon, Fielder, Collins & Mott) PDF tax sale scraper.

Covers: Brazoria, Chambers, Fort Bend (Pcts 2/3/4), Harris (Pcts 1/2/3/4/5/7/8)
PDFs at: https://www.pbfcm.com/docs/taxdocs/sales/{MM}-2026{county}taxsale.pdf
"""
import re
import logging
import httpx
import io
from pypdf import PdfReader
from typing import List, Dict

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
PDF_BASE = "https://www.pbfcm.com/docs/taxdocs/sales"

PRECINCT_MAP = {
    "harris":    ["harrispct1", "harrispct2", "harrispct3", "harrispct4", "harrispct5", "harrispct7", "harrispct8"],
    "fort_bend": ["ftbendpct2", "ftbendpct3", "ftbendpct4"],
}
SINGLE_PDFS = {
    "brazoria": "brazoria",
    "chambers": "chambers",
}


def fetch_pdf(url: str) -> bytes:
    resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=60)
    resp.raise_for_status()
    return resp.content


def parse_pbfcm_pdf(content: bytes, county: str) -> List[Dict]:
    """Parse PBFCM tax sale PDF. Items are delimited by 'ItemNo CauseNo-T' pattern."""
    reader = PdfReader(io.BytesIO(content))
    full_text = "\n".join(page.extract_text() for page in reader.pages)

    # Split into item blocks — each starts with a number followed by a Cause No like "12345-T"
    item_blocks = re.split(r'\n(?=\d+\s+\d{5,8}-T)', full_text)
    records = []

    for block in item_blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue

        # First line: "ItemNo CauseNo-T"
        first = lines[0]
        cause_match = re.search(r"(\d{5,8}-T)", first)
        if not cause_match:
            continue

        cause_no = cause_match.group(1)
        item_no = first.split()[0] if first.split() else ""

        # Join all lines into a single text for easier searching
        text = " ".join(lines).replace("\n", " ")

        # Extract owner: between "VS." and next known marker
        owner = ""
        vs_match = re.search(r"VS\.\s*(.+?)(?:\d+\s+ACRE|\d+\.\d+\s+ACRES|TRACT|LOT|PROPERTY|Adjudged)", text, re.IGNORECASE)
        if vs_match:
            owner = vs_match.group(1).strip().strip(",")
            # Capitalize properly
            owner = re.sub(r'\s+', ' ', owner).strip()

        # Extract Adjudged Value
        adj_match = re.search(r"Adjudged\s*Value:\s*\$?([\d,]+\.?\d*)", text)
        appraised_value = float(adj_match.group(1).replace(",", "")) if adj_match else 0

        # Extract Geographic ID (parcel) — pattern like 2986-0034-000 or 0222-0022-110
        geo_match = re.search(r"(\d{4}-\d{3,7}-\d{3,6})", text)
        parcel_id = geo_match.group(1) if geo_match else ""

        # Extract Minimum Bid — the dollar amount after the GEO ID
        bid_match = re.search(rf"{re.escape(parcel_id)}\s*\$?([\d,]+\.?\d*)", text) if parcel_id else None
        min_bid = float(bid_match.group(1).replace(",", "")) if bid_match else 0

        # Extract tax years due
        tax_match = re.search(r"((?:\d{4}[-–]\d{4}\s*)+)Taxes?\s*Due", text)
        tax_years = tax_match.group(1).strip() if tax_match else ""

        records.append({
            "parcel_id": parcel_id,
            "owner_name": owner,
            "address": "",
            "appraised_value": appraised_value,
            "min_bid": min_bid,
            "est_tax_due": min_bid,
            "tax_years_due": tax_years,
            "cause_no": cause_no,
            "item_no": item_no,
            "source": "pbfcm",
            "county": county,
            "is_delinquent": True,
            "on_auction_list": True,
        })

    return records


def ingest_county(county: str) -> List[Dict]:
    """Ingest PBFCM tax sale data for a single county."""
    records = []

    if county in SINGLE_PDFS:
        url = f"{PDF_BASE}/06-2026{SINGLE_PDFS[county]}taxsale.pdf"
        try:
            content = fetch_pdf(url)
            records = parse_pbfcm_pdf(content, county)
            logging.info(f"[{county}/pbfcm] {len(records)} records")
        except Exception as e:
            logging.warning(f"[{county}/pbfcm] failed: {e}")

    precincts = PRECINCT_MAP.get(county, [])
    for p in precincts:
        url = f"{PDF_BASE}/06-2026{p}taxsale.pdf"
        try:
            content = fetch_pdf(url)
            recs = parse_pbfcm_pdf(content, county)
            records.extend(recs)
            logging.info(f"[{county}/pbfcm/{p}] {len(recs)} records")
        except Exception as e:
            logging.warning(f"[{county}/pbfcm/{p}] failed: {e}")

    # Deduplicate by parcel_id, prefer items with parcel_id
    seen = {}
    for r in records:
        pid = r.get("parcel_id") or r.get("cause_no", "")
        if pid:
            if pid not in seen or (r.get("parcel_id") and not seen[pid].get("parcel_id")):
                seen[pid] = r
    return list(seen.values())
