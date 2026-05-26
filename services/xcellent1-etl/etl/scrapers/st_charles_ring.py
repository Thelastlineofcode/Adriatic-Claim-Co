"""
St. Charles Parish — secondary ring for Xcellent1.
Destrehan, Luling, Hahnville border the western edge of St. John.
Shares same adjudicated property process. Xcellent1 may expand service routes here.

Sources:
  - lataxauction.com/?parish=st-charles
  - stcharlesgov.net adjudicated list (shared with Grandee's pipeline)

NOTE: If Grandee's ETL is running, this data is already being pulled.
This scraper exists as a standalone fallback for Xcellent1-specific scheduling.
"""
import logging
import asyncio
from typing import List, Dict
from etl.crawler import Crawler

logger = logging.getLogger(__name__)
PARISH = "st_charles"
STATE = "LA"


def ingest() -> List[Dict]:
    async def _run():
        async with Crawler() as c:
            rows = await c.extract_table(
                "https://lataxauction.com/auctions/?parish=st-charles",
                table_selector="table",
                wait_for="table, .auction-list",
                paginate_selector=".next-page, a:has-text('Next')",
                max_pages=15,
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
                "acquisition_priority": "MEDIUM",
                "in_service_zone": False,
            })
        logger.info(f"[st_charles_ring] {len(records)} records")
        return records

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(_run())
    loop.close()
    return result
