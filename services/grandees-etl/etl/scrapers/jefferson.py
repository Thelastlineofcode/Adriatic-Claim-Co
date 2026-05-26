"""
Jefferson Parish, Louisiana — secondary ring for Grandee's.
High-volume adjudicated property list. West Bank commercial targets.

Sources:
  - jeffersonparish.net tax sale / adjudicated listings
  - lataxauction.com/?parish=jefferson
"""
import logging
from typing import List, Dict
from etl.crawler import Crawler
import asyncio

logger = logging.getLogger(__name__)
PARISH = "jefferson"
STATE = "LA"


def ingest() -> List[Dict]:
    async def _run():
        async with Crawler() as c:
            rows = await c.extract_table(
                "https://lataxauction.com/auctions/?parish=jefferson",
                table_selector="table",
                wait_for="table, .auction-list",
                paginate_selector=".next-page, a:has-text('Next')",
                max_pages=30,
            )
        records = []
        for row in rows:
            records.append({
                "parcel_id": row.get("parcel", row.get("account_number", "")).strip(),
                "owner_name": row.get("owner", "").strip(),
                "address": row.get("address", row.get("location", "")).strip(),
                "min_bid": row.get("minimum_bid", "0").strip(),
                "auction_date": row.get("sale_date", "").strip(),
                "source": "lataxauction",
                "parish": PARISH,
                "state": STATE,
                "is_delinquent": True,
                "is_adjudicated": True,
                "on_auction_list": True,
            })
        logger.info(f"[jefferson] {len(records)} records")
        return records

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(_run())
    loop.close()
    return result
