"""
Harris County — PRIMARY county, full Gulf Coast anchor.

Sources (in priority order):
  1. HCAD bulk property data download (FREE flat files, full county)
     https://hcad.org/pdata/pdata-property-downloads.html
  2. hctax.net delinquent tax list
     https://www.hctax.net/Property/TaxSales
  3. caopay.harriscountytx.gov — delinquent account search
  4. mvbalaw.com — monthly Harris County auction list
  5. foreclosehouston.com — pre-sale list

HCAD bulk files (updated annually/quarterly):
  - real_acct.txt      : property accounts, values, owner info
  - delinquent.txt     : delinquent accounts (if available)
  - land.txt           : land data
  Download all at: https://hcad.org/pdata/pdata-property-downloads.html
"""
import os
import zipfile
import logging
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AdriaticClaimCo/1.0)"}
HCAD_BULK_URL = "https://hcad.org/pdata/pdata-property-downloads.html"
HCAD_DATA_DIR = os.path.join(os.getenv("DATA_DIR", "./data"), "hcad")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_html(url: str) -> str:
    resp = httpx.get(url, headers=HEADERS, timeout=60, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30))
def download_file(url: str, dest: str):
    """Stream download a large file."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with httpx.stream("GET", url, headers=HEADERS, timeout=300, follow_redirects=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=65536):
                f.write(chunk)


def get_hcad_bulk_links() -> Dict[str, str]:
    """Scrape HCAD download page for current bulk file URLs."""
    try:
        html = fetch_html(HCAD_BULK_URL)
        soup = BeautifulSoup(html, "lxml")
        links = {}
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True).lower()
            if ".zip" in href.lower() or ".txt" in href.lower():
                if "real" in text or "acct" in text:
                    links["real_acct"] = href if href.startswith("http") else f"https://hcad.org{href}"
                elif "land" in text:
                    links["land"] = href if href.startswith("http") else f"https://hcad.org{href}"
                elif "delinquent" in text:
                    links["delinquent"] = href if href.startswith("http") else f"https://hcad.org{href}"
        logging.info(f"[harris/hcad] found bulk links: {list(links.keys())}")
        return links
    except Exception as e:
        logging.warning(f"[harris/hcad] failed to get bulk links: {e}")
        return {}


def parse_hcad_real_acct(filepath: str) -> List[Dict]:
    """
    Parse HCAD real_acct.txt pipe-delimited file.
    Key columns: account, owner_name, situs_street, situs_city,
                 appraised_value, total_value, exemption_codes
    HCAD column order varies by year — parse header row.
    """
    records = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            header = None
            for i, line in enumerate(f):
                cols = line.strip().split("|")
                if i == 0:
                    header = [c.strip().lower() for c in cols]
                    continue
                if not header or len(cols) < 5:
                    continue
                row = dict(zip(header, cols))
                records.append({
                    "parcel_id": row.get("account", "").strip(),
                    "owner_name": row.get("owner_name", "").strip(),
                    "address": f"{row.get('situs_num','').strip()} {row.get('situs_street','').strip()} {row.get('situs_street_sfx','').strip()}".strip(),
                    "city": row.get("situs_city", "HOUSTON").strip(),
                    "appraised_value": float(row.get("appraised_val", "0").replace(",", "") or 0),
                    "est_tax_due": 0.0,
                    "is_delinquent": False,
                    "on_auction_list": False,
                    "source": "hcad_bulk",
                    "county": "harris",
                })
        logging.info(f"[harris/hcad] parsed {len(records):,} property records")
    except Exception as e:
        logging.error(f"[harris/hcad] parse error: {e}")
    return records


def enrich_delinquent(records: List[Dict], delinquent_path: str) -> List[Dict]:
    """Cross-reference bulk records against delinquent file."""
    delinquent_set = {}
    try:
        with open(delinquent_path, "r", encoding="utf-8", errors="replace") as f:
            header = None
            for i, line in enumerate(f):
                cols = line.strip().split("|")
                if i == 0:
                    header = [c.strip().lower() for c in cols]
                    continue
                if not header:
                    continue
                row = dict(zip(header, cols))
                acct = row.get("account", "").strip()
                amt = float(row.get("amount_due", "0").replace(",", "") or 0)
                delinquent_set[acct] = amt
        logging.info(f"[harris] loaded {len(delinquent_set):,} delinquent accounts")
    except Exception as e:
        logging.warning(f"[harris] delinquent enrich failed: {e}")
    for r in records:
        if r["parcel_id"] in delinquent_set:
            r["is_delinquent"] = True
            r["est_tax_due"] = delinquent_set[r["parcel_id"]]
    return records


def scrape_hctax_auction() -> List[Dict]:
    """Scrape hctax.net tax sale listing."""
    url = "https://www.hctax.net/Property/TaxSales"
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "lxml")
        records = []
        for row in soup.select("table tr")[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 3:
                records.append({
                    "parcel_id": cols[0],
                    "address": cols[1] if len(cols) > 1 else "",
                    "min_bid": cols[2] if len(cols) > 2 else "0",
                    "auction_date": cols[3] if len(cols) > 3 else None,
                    "owner_name": cols[4] if len(cols) > 4 else "",
                    "source": "hctax_auction",
                    "county": "harris",
                    "is_delinquent": True,
                    "on_auction_list": True,
                })
        logging.info(f"[harris/hctax] {len(records)} auction records")
        return records
    except Exception as e:
        logging.warning(f"[harris/hctax] failed: {e}")
        return []


def scrape_mvba_harris() -> List[Dict]:
    url = "https://mvbalaw.com/tax-sales/harris-county/"
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "lxml")
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
                    "county": "harris",
                    "is_delinquent": True,
                    "on_auction_list": True,
                })
        logging.info(f"[harris/mvba] {len(records)} records")
        return records
    except Exception as e:
        logging.warning(f"[harris/mvba] failed: {e}")
        return []


def scrape_foreclose_houston() -> List[Dict]:
    url = "https://www.foreclosehouston.com/products/free-tax-list"
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "lxml")
        records = []
        for row in soup.select("table tr")[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 2:
                records.append({
                    "parcel_id": cols[0],
                    "address": cols[1] if len(cols) > 1 else "",
                    "est_tax_due": cols[2] if len(cols) > 2 else "0",
                    "source": "foreclose_houston",
                    "county": "harris",
                    "is_delinquent": True,
                    "on_auction_list": False,
                })
        logging.info(f"[harris/foreclose] {len(records)} records")
        return records
    except Exception as e:
        logging.warning(f"[harris/foreclose] failed: {e}")
        return []


def ingest(use_bulk: bool = True) -> List[Dict]:
    """
    Main Harris ingest.
    use_bulk=True: download HCAD bulk files (full county, ~500MB, best for nightly)
    use_bulk=False: scrape only auction + delinquent lists (fast, lighter)
    """
    records = []

    if use_bulk:
        os.makedirs(HCAD_DATA_DIR, exist_ok=True)
        links = get_hcad_bulk_links()
        real_path = os.path.join(HCAD_DATA_DIR, "real_acct.zip")
        delinq_path = os.path.join(HCAD_DATA_DIR, "delinquent.zip")

        if "real_acct" in links:
            logging.info("[harris] downloading HCAD bulk real_acct...")
            download_file(links["real_acct"], real_path)
            with zipfile.ZipFile(real_path, "r") as z:
                txt_files = [n for n in z.namelist() if n.endswith(".txt")]
                if txt_files:
                    z.extract(txt_files[0], HCAD_DATA_DIR)
                    records = parse_hcad_real_acct(os.path.join(HCAD_DATA_DIR, txt_files[0]))

        if "delinquent" in links:
            logging.info("[harris] downloading HCAD delinquent file...")
            download_file(links["delinquent"], delinq_path)
            with zipfile.ZipFile(delinq_path, "r") as z:
                txt_files = [n for n in z.namelist() if n.endswith(".txt")]
                if txt_files:
                    z.extract(txt_files[0], HCAD_DATA_DIR)
                    records = enrich_delinquent(records, os.path.join(HCAD_DATA_DIR, txt_files[0]))

    # Always layer in live auction + delinquent scrapes on top
    auction_records = scrape_hctax_auction() + scrape_mvba_harris() + scrape_foreclose_houston()

    # Merge: auction records override bulk records for same parcel
    index = {r["parcel_id"]: r for r in records if r.get("parcel_id")}
    for ar in auction_records:
        pid = ar.get("parcel_id", "")
        if pid in index:
            index[pid].update({k: v for k, v in ar.items() if v})
        else:
            index[pid] = ar

    result = list(index.values())
    distress = [r for r in result if r.get("is_delinquent") or r.get("on_auction_list") or r.get("appraised_value", 999999) < 200000]
    logging.info(f"[harris] final distress candidates: {len(distress):,} of {len(result):,} total")
    return distress
