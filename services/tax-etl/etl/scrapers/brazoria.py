"""
Brazoria County — SE Houston / Gulf Coast.
Sources:
  - brazoriacad.org
  - mvbalaw.com/tax-sales/brazoria-county/
  - brazoriacountytx.gov delinquent tax roll
"""
import logging
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AdriaticClaimCo/1.0)"}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_html(url: str) -> str:
    resp = httpx.get(url, headers=HEADERS, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def scrape_mvba() -> List[Dict]:
    url = "https://mvbalaw.com/tax-sales/brazoria-county/"
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "lxml")
        records = []
        for row in soup.select("table tr")[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 3:
                records.append({
                    "parcel_id": cols[0],
                    "owner_name": cols[1],
                    "address": cols[2],
                    "min_bid": cols[3] if len(cols) > 3 else "0",
                    "auction_date": cols[4] if len(cols) > 4 else None,
                    "source": "mvba_auction",
                    "county": "brazoria",
                    "is_delinquent": True,
                    "on_auction_list": True,
                })
        logging.info(f"[brazoria/mvba] {len(records)} records")
        return records
    except Exception as e:
        logging.warning(f"[brazoria/mvba] failed: {e}")
        return []


def scrape_brazoria_delinquent() -> List[Dict]:
    """Brazoria County delinquent tax roll (public HTML)."""
    url = "https://www.brazoriacountytx.gov/departments/tax-office/property-taxes/delinquent-tax-roll"
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "lxml")
        records = []
        for row in soup.select("table tr")[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 2:
                records.append({
                    "parcel_id": cols[0],
                    "owner_name": cols[1] if len(cols) > 1 else "",
                    "address": cols[2] if len(cols) > 2 else "",
                    "est_tax_due": cols[3] if len(cols) > 3 else "0",
                    "source": "brazoria_delinquent",
                    "county": "brazoria",
                    "is_delinquent": True,
                    "on_auction_list": False,
                })
        logging.info(f"[brazoria/delinquent] {len(records)} records")
        return records
    except Exception as e:
        logging.warning(f"[brazoria/delinquent] failed: {e}")
        return []


def ingest() -> List[Dict]:
    records = []
    records.extend(scrape_mvba())
    records.extend(scrape_brazoria_delinquent())
    seen = {}
    for r in records:
        pid = r.get("parcel_id") or r.get("address", "")
        if pid not in seen or r.get("on_auction_list"):
            seen[pid] = r
    return list(seen.values())
