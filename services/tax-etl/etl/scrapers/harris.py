"""
Harris County — PRIMARY county, full Gulf Coast anchor.

Sources:
  - PBFCM tax sale PDFs (Pcts 1/2/3/4/5/7/8, confirmed working)
  - HCAD bulk property data (Playwright for JS-loaded links)
  - hctax.net auction list
"""
import os
import zipfile
import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from etl.scrapers.pbfcm import ingest_county as pbfcm_ingest

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
HCAD_BULK_URL = "https://hcad.org/pdata/pdata-property-downloads.html"
HCAD_DATA_DIR = os.path.join(os.getenv("DATA_DIR", "./data"), "hcad")
HCAD_CACHE = os.path.join(HCAD_DATA_DIR, "real_acct.txt")


def get_hcad_bulk_links_playwright() -> Dict[str, str]:
    """Use Playwright to get HCAD bulk download links (JS-rendered page)."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(HCAD_BULK_URL, timeout=120000)
            page.wait_for_load_state("networkidle", timeout=120000)
            links = {}
            for a in page.query_selector_all("a[href]"):
                href = a.get_attribute("href") or ""
                text = (a.inner_text() or "").lower()
                if ".zip" in href.lower():
                    full = href if href.startswith("http") else f"https://hcad.org{href}"
                    if "real" in text or "acct" in text:
                        links["real_acct"] = full
                    elif "land" in text:
                        links["land"] = full
                    elif "delinquent" in text:
                        links["delinquent"] = full
            browser.close()
            logging.info(f"[harris/hcad] PW bulk links: {list(links.keys())}")
            return links
    except Exception as e:
        logging.warning(f"[harris/hcad] Playwright failed: {e}")
        return {}


def download_file(url: str, dest: str):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with httpx.stream("GET", url, headers=HEADERS, timeout=300, follow_redirects=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=65536):
                f.write(chunk)


def parse_hcad_real_acct(filepath: str) -> List[Dict]:
    records = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            header = None
            for i, line in enumerate(f):
                cols = line.strip().split("\t")
                if i == 0:
                    header = [c.strip().lower() for c in cols]
                    continue
                if not header or len(cols) < 5:
                    continue
                row = dict(zip(header, cols))
                acct = row.get("acct", "").strip()
                if not acct:
                    continue
                try:
                    appr_val = float(str(row.get("tot_appr_val", "0")).replace(",", "") or 0)
                except ValueError:
                    appr_val = 0
                records.append({
                    "parcel_id": acct,
                    "owner_name": row.get("mailto", "").strip(),
                    "address": row.get("site_addr_1", "").strip(),
                    "city": "",
                    "appraised_value": appr_val,
                    "est_tax_due": 0,
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
    delinquent_set = {}
    try:
        with open(delinquent_path, "r", encoding="utf-8", errors="replace") as f:
            header = None
            for i, line in enumerate(f):
                cols = line.strip().split("|")
                if i == 0:
                    header = [c.strip().lower() for c in cols]
                    continue
                if not header or len(cols) < 2:
                    continue
                row = dict(zip(header, cols))
                acct = row.get("account", "").strip()
                amt = float(row.get("amount_due", "0").replace(",", "") or 0)
                if acct:
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
    """Scrape hctax.net tax sale listing (uses Playwright for JS table)."""
    url = "https://www.hctax.net/Property/TaxSales"
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            records = []
            rows = page.query_selector_all("table tr")
            for row in rows[1:]:
                cells = row.query_selector_all("td")
                cols = [cell.inner_text().strip() for cell in cells]
                if len(cols) >= 3:
                    records.append({
                        "parcel_id": cols[0],
                        "address": cols[1] if len(cols) > 1 else "",
                        "min_bid": cols[2] if len(cols) > 2 else "0",
                        "owner_name": cols[4] if len(cols) > 4 else "",
                        "source": "hctax_auction",
                        "county": "harris",
                        "is_delinquent": True,
                        "on_auction_list": True,
                    })
            browser.close()
            logging.info(f"[harris/hctax] {len(records)} auction records")
            return records
    except Exception as e:
        logging.warning(f"[harris/hctax] failed: {e}")
        return []


def scrape_foreclose_houston() -> List[Dict]:
    url = "https://www.foreclosehouston.com/products/free-tax-list"
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            records = []
            rows = page.query_selector_all("table tr")
            for row in rows[1:]:
                cells = row.query_selector_all("td")
                cols = [cell.inner_text().strip() for cell in cells]
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
            browser.close()
            logging.info(f"[harris/foreclose] {len(records)} records")
            return records
    except Exception as e:
        logging.warning(f"[harris/foreclose] failed: {e}")
        return []


def ingest(use_bulk: bool = True) -> List[Dict]:
    records = []

    if use_bulk and os.path.exists(HCAD_CACHE):
        logging.info("[harris] using cached HCAD bulk data")
        records = parse_hcad_real_acct(HCAD_CACHE)
    elif use_bulk:
        os.makedirs(HCAD_DATA_DIR, exist_ok=True)
        links = get_hcad_bulk_links_playwright()
        if "real_acct" in links:
            real_zip = os.path.join(HCAD_DATA_DIR, "real_acct.zip")
            logging.info("[harris] downloading HCAD bulk...")
            download_file(links["real_acct"], real_zip)
            with zipfile.ZipFile(real_zip, "r") as z:
                target = "real_acct.txt"
                if target in z.namelist():
                    z.extract(target, HCAD_DATA_DIR)
                    records = parse_hcad_real_acct(os.path.join(HCAD_DATA_DIR, target))
                else:
                    txt_files = [n for n in z.namelist() if n.endswith(".txt")]
                    if txt_files:
                        z.extract(txt_files[0], HCAD_DATA_DIR)
                        records = parse_hcad_real_acct(os.path.join(HCAD_DATA_DIR, txt_files[0]))

        if "delinquent" in links:
            delinq_zip = os.path.join(HCAD_DATA_DIR, "delinquent.zip")
            logging.info("[harris] downloading HCAD delinquent...")
            download_file(links["delinquent"], delinq_zip)
            with zipfile.ZipFile(delinq_zip, "r") as z:
                txt_files = [n for n in z.namelist() if n.endswith(".txt")]
                if txt_files:
                    z.extract(txt_files[0], HCAD_DATA_DIR)
                    records = enrich_delinquent(records, os.path.join(HCAD_DATA_DIR, txt_files[0]))

    auction_records = pbfcm_ingest("harris") + scrape_hctax_auction() + scrape_foreclose_houston()

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
