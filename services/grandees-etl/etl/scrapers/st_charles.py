"""
St. Charles Parish, Louisiana — PRIMARY parish for Grandee's.

St. Charles Parish is NOT a standard tax lien/deed state — Louisiana uses
'adjudicated property' (tax-delinquent parcels the parish has taken title to).
These are the primary acquisition targets.

Sources (in priority order):
  1. St. Charles Parish Assessor — parcel/property search
     https://www.stcharlesassessor.org
  2. St. Charles Parish Govt — adjudicated property lists + tax sale notices
     https://www.stcharlesgov.net
  3. Louisiana Tax Commission adjudicated property portal
     https://revenue.louisiana.gov/LandSales
  4. lataxauction.com — aggregated LA adjudicated auctions
     https://lataxauction.com
"""
import logging
from typing import List, Dict
from etl.crawler import Crawler, run_async
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

PARISH = "st_charles"
STATE = "LA"


async def _scrape_assessor() -> List[Dict]:
    """St. Charles Parish Assessor property search."""
    async with Crawler() as c:
        html = await c.get(
            "https://www.stcharlesassessor.org/property-search",
            wait_for="table, .results, #searchResults",
        )
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    records = []
    for row in soup.select("table tr")[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) >= 3:
            records.append({
                "parcel_id": cols[0],
                "owner_name": cols[1] if len(cols) > 1 else "",
                "address": cols[2] if len(cols) > 2 else "",
                "appraised_value": cols[3] if len(cols) > 3 else "0",
                "source": "st_charles_assessor",
                "parish": PARISH,
                "state": STATE,
                "is_delinquent": False,
                "is_adjudicated": False,
            })
    logger.info(f"[st_charles/assessor] {len(records)} records")
    return records


async def _scrape_adjudicated() -> List[Dict]:
    """St. Charles Parish adjudicated (tax-delinquent, parish-owned) properties."""
    async with Crawler() as c:
        rows = await c.extract_table(
            "https://www.stcharlesgov.net/government/departments/parish-council/adjudicated-properties",
            table_selector="table",
            wait_for="table",
            paginate_selector="a:has-text('Next'), .pagination-next, [aria-label='Next']",
            max_pages=30,
        )
    records = []
    for row in rows:
        records.append({
            "parcel_id": row.get("parcel_id", row.get("account", "")).strip(),
            "owner_name": row.get("owner", row.get("owner_name", "")).strip(),
            "address": row.get("address", row.get("location", "")).strip(),
            "est_tax_due": row.get("amount_due", row.get("taxes_owed", "0")).strip(),
            "source": "st_charles_adjudicated",
            "parish": PARISH,
            "state": STATE,
            "is_delinquent": True,
            "is_adjudicated": True,
        })
    logger.info(f"[st_charles/adjudicated] {len(records)} records")
    return records


async def _scrape_lataxauction() -> List[Dict]:
    """lataxauction.com — St. Charles Parish filter."""
    async with Crawler() as c:
        rows = await c.extract_table(
            "https://lataxauction.com/auctions/?parish=st-charles",
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
    logger.info(f"[st_charles/lataxauction] {len(records)} records")
    return records


def ingest() -> List[Dict]:
    import asyncio
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
    logger.info(f"[st_charles] distress candidates: {len(distress):,} of {len(result):,}")
    return distress
