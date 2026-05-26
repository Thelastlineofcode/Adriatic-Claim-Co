"""
Harris County tax lien data ingest.
Sources:
  1. caopay.harriscountytx.gov — delinquent accounts
  2. mvbalaw.com — monthly auction list (Harris)
  3. foreclosehouston.com — pre-sale list
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

def scrape_mvba_harris() -> List[Dict]:
    """
    Scrape mvbalaw.com Harris County monthly auction list.
    Returns list of dicts with: address, parcel_id, min_bid, auction_date, county
    """
    url = "https://mvbalaw.com/tax-sales/harris-county/"
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "lxml")
        records = []
        # mvbalaw tables: account#, owner, address, city, min bid, auction date
        for row in soup.select("table tr")[1:]:  # skip header
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 5:
                records.append({
                    "parcel_id": cols[0],
                    "owner_name": cols[1],
                    "address": cols[2],
                    "city": cols[3],
                    "min_bid": cols[4],
                    "auction_date": cols[5] if len(cols) > 5 else None,
                    "source": "mvba_auction",
                    "county": "harris",
                    "on_auction_list": True,
                    "is_delinquent": True,
                })
        logging.info(f"[harris/mvba] scraped {len(records)} auction records")
        return records
    except Exception as e:
        logging.warning(f"[harris/mvba] failed: {e}")
        return []

def scrape_foreclose_houston() -> List[Dict]:
    """
    Scrape foreclosehouston.com free tax list.
    """
    url = "https://www.foreclosehouston.com/products/free-tax-list"
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "lxml")
        records = []
        for row in soup.select("table tr")[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 3:
                records.append({
                    "parcel_id": cols[0] if cols else None,
                    "address": cols[1] if len(cols) > 1 else None,
                    "est_tax_due": cols[2] if len(cols) > 2 else None,
                    "source": "foreclose_houston",
                    "county": "harris",
                    "is_delinquent": True,
                    "on_auction_list": False,
                })
        logging.info(f"[harris/foreclose] scraped {len(records)} records")
        return records
    except Exception as e:
        logging.warning(f"[harris/foreclose] failed: {e}")
        return []

def ingest() -> List[Dict]:
    """Main Harris County ingest — merges all sources."""
    records = []
    records.extend(scrape_mvba_harris())
    records.extend(scrape_foreclose_houston())
    # Deduplicate by parcel_id — auction list wins
    seen = {}
    for r in records:
        pid = r.get("parcel_id") or r.get("address", "")
        if pid not in seen or r.get("on_auction_list"):
            seen[pid] = r
    return list(seen.values())
