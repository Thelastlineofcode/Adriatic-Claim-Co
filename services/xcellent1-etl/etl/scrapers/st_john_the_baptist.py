"""
St. John the Baptist Parish, Louisiana — PRIMARY parish for Xcellent1.
LaPlace is the parish seat. Xcellent1 lawn care operates throughout this parish.

Louisiana adjudicated property process — same as Grandee's (St. Charles).
See grandees-etl/docs/LOUISIANA_NOTES.md for full process details.

Sources (in priority order):
  1. St. John the Baptist Parish Assessor
     https://www.sjbassessor.org
  2. St. John Parish Government — adjudicated property + tax sale notices
     https://www.stjohnla.gov
  3. lataxauction.com — St. John the Baptist Parish filter
     https://lataxauction.com/auctions/?parish=st-john-the-baptist
  4. Louisiana Tax Commission land sales
     https://revenue.louisiana.gov/LandSales
"""
import logging
import asyncio
from typing import List, Dict
from etl.crawler import Crawler
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

PARISH = "st_john_the_baptist"
STATE = "LA"

# Xcellent1 service area ZIPs in St. John the Baptist Parish
XCELLENT1_SERVICE_ZIPS = {
    "70068",  # LaPlace
    "70084",  # Reserve
    "70051",  # Garyville
    "70049",  # Edgard (west bank)
    "70052",  # Gramercy (St. James border)
}


async def _scrape_assessor() -> List[Dict]:
    """St. John the Baptist Parish Assessor property search."""
    async with Crawler() as c:
        html = await c.get(
            "https://www.sjbassessor.org",
            wait_for="table, .results, form",
        )
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    records = []
    for row in soup.select("table tr")[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) >= 2:
            records.append({
                "parcel_id": cols[0],
                "owner_name": cols[1] if len(cols) > 1 else "",
                "address": cols[2] if len(cols) > 2 else "",
                "appraised_value": cols[3] if len(cols) > 3 else "0",
                "source": "sjb_assessor",
                "parish": PARISH,
                "state": STATE,
                "is_delinquent": False,
                "is_adjudicated": False,
            })
    logger.info(f"[st_john/assessor] {len(records)} records")
    return records


async def _scrape_adjudicated() -> List[Dict]:
    """St. John Parish Government — adjudicated property list."""
    async with Crawler() as c:
        rows = await c.extract_table(
            "https://www.stjohnla.gov/government/adjudicated-properties",
            table_selector="table",
            wait_for="table",
            paginate_selector="a:has-text('Next'), .pagination-next",
            max_pages=20,
        )
    records = []
    for row in rows:
        records.append({
            "parcel_id": row.get("parcel_id", row.get("account", "")).strip(),
            "owner_name": row.get("owner", row.get("owner_name", "")).strip(),
            "address": row.get("address", row.get("location", "")).strip(),
            "est_tax_due": row.get("amount_due", row.get("taxes_owed", "0")).strip(),
            "source": "stjohn_adjudicated",
            "parish": PARISH,
            "state": STATE,
            "is_delinquent": True,
            "is_adjudicated": True,
        })
    logger.info(f"[st_john/adjudicated] {len(records)} records")
    return records


async def _scrape_lataxauction() -> List[Dict]:
    """lataxauction.com — St. John the Baptist Parish."""
    async with Crawler() as c:
        rows = await c.extract_table(
            "https://lataxauction.com/auctions/?parish=st-john-the-baptist",
            table_selector="table",
            wait_for="table, .auction-list",
            paginate_selector=".next-page, a:has-text('Next')",
            max_pages=10,
        )
    records = []
    for row in rows:
        records.append({
            "parcel_id": row.get("parcel", row.get("account_number", "")).strip(),
            "owner_name": row.get("owner", "").strip(),
            "address": row.get("address", row.get("location", "")).strip(),
            "min_bid": row.get("minimum_bid", row.get("opening_bid", "0")).strip(),
            "auction_date": row.get("sale_date", row.get("auction_date", "")).strip(),
            "source": "lataxauction",
            "parish": PARISH,
            "state": STATE,
            "is_delinquent": True,
            "is_adjudicated": True,
            "on_auction_list": True,
        })
    logger.info(f"[st_john/lataxauction] {len(records)} records")
    return records


def _tag_service_zone(records: List[Dict]) -> List[Dict]:
    """Flag records within Xcellent1 service ZIPs."""
    for r in records:
        zip_code = r.get("zip", r.get("zip_code", "")).strip()
        in_zone = zip_code in XCELLENT1_SERVICE_ZIPS
        r["in_service_zone"] = in_zone
        r["acquisition_priority"] = "HIGH" if in_zone else "MEDIUM"
    return records


def ingest() -> List[Dict]:
    loop = asyncio.new_event_loop()

    async def _run():
        assessor = await _scrape_assessor()
        adjudicated = await _scrape_adjudicated()
        auction = await _scrape_lataxauction()
        return assessor, adjudicated, auction

    assessor, adjudicated, auction = loop.run_until_complete(_run())
    loop.close()

    index = {r["parcel_id"]: r for r in assessor if r.get("parcel_id")}
    for r in adjudicated + auction:
        pid = r.get("parcel_id", "")
        if pid in index:
            index[pid].update({k: v for k, v in r.items() if v})
        else:
            index[pid] = r

    result = list(index.values())
    distress = [r for r in result if r.get("is_adjudicated") or r.get("is_delinquent") or r.get("on_auction_list")]
    distress = _tag_service_zone(distress)
    logger.info(f"[st_john] distress candidates: {len(distress):,} of {len(result):,}")
    return distress
