"""
Bell County tax lien data ingest.
Sources:
  1. bellcad.org/data-portal — bulk export (preferred)
  2. esearch.bellcad.org — individual property scrape (fallback)
  3. mvbalaw.com — Bell County auction list
"""
import logging
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict
import csv
import io

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AdriaticClaimCo/1.0)"}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch(url: str, **kwargs) -> httpx.Response:
    return httpx.get(url, headers=HEADERS, timeout=30, follow_redirects=True, **kwargs)

def scrape_bellcad_portal() -> List[Dict]:
    """Try Bell CAD data portal bulk CSV export first."""
    try:
        resp = fetch("https://bellcad.org/data-portal/")
        # Attempt to find CSV download links
        soup = BeautifulSoup(resp.text, "lxml")
        csv_links = [a["href"] for a in soup.find_all("a", href=True) if ".csv" in a["href"].lower()]
        if csv_links:
            csv_resp = fetch(csv_links[0])
            reader = csv.DictReader(io.StringIO(csv_resp.text))
            records = []
            for row in reader:
                records.append({
                    "parcel_id": row.get("Account") or row.get("ParcelID"),
                    "owner_name": row.get("OwnerName") or row.get("Owner"),
                    "address": row.get("SitusAddress") or row.get("Address"),
                    "appraised_value": row.get("AppraisedValue") or row.get("TotalValue"),
                    "est_tax_due": row.get("EstTaxDue") or row.get("TaxDue"),
                    "source": "bellcad_portal",
                    "county": "bell",
                    "is_delinquent": False,  # enriched later from delinquent roll
                    "on_auction_list": False,
                })
            logging.info(f"[bell/portal] {len(records)} records from bulk export")
            return records
    except Exception as e:
        logging.warning(f"[bell/portal] failed: {e}")
    return []

def scrape_mvba_bell() -> List[Dict]:
    """Scrape mvbalaw.com Bell County auction list."""
    url = "https://mvbalaw.com/tax-sales/bell-county/"
    try:
        resp = fetch(url)
        soup = BeautifulSoup(resp.text, "lxml")
        records = []
        for row in soup.select("table tr")[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 4:
                records.append({
                    "parcel_id": cols[0],
                    "owner_name": cols[1],
                    "address": cols[2],
                    "min_bid": cols[3],
                    "auction_date": cols[4] if len(cols) > 4 else None,
                    "source": "mvba_auction",
                    "county": "bell",
                    "is_delinquent": True,
                    "on_auction_list": True,
                })
        logging.info(f"[bell/mvba] {len(records)} auction records")
        return records
    except Exception as e:
        logging.warning(f"[bell/mvba] failed: {e}")
        return []

def ingest() -> List[Dict]:
    records = []
    records.extend(scrape_bellcad_portal())
    records.extend(scrape_mvba_bell())
    seen = {}
    for r in records:
        pid = r.get("parcel_id") or r.get("address", "")
        if pid not in seen or r.get("on_auction_list"):
            seen[pid] = r
    return list(seen.values())
