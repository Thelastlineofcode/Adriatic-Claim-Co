"""
St. James Parish — secondary ring for Xcellent1.
Lutcher and Gramercy sit on the St. John border.
Very low investor competition. Small parish, adjudicated list is short but high-value.

Sources:
  - lataxauction.com/?parish=st-james
  - stjamesla.gov
"""
import logging
import asyncio
from typing import List, Dict
from etl.crawler import Crawler

logger = logging.getLogger(__name__)
PARISH = "st_james"
STATE = "LA"


def ingest() -> List[Dict]:
    async def _run():
        async with Crawler() as c:
            rows = await c.extract_table(
                "https://lataxauction.com/auctions/?parish=st-james",
                table_selector="table",
                wait_for="table, .auction-list",
                paginate_selector=".next-page, a:has-text('Next')",
                max_pages=10,
            )
        records = []
        for row in rows:
            records.append({
                "parcel_id": row.get("parcel", "").strip(),
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
        logger.info(f"[st_james] {len(records)} records")
        return records

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(_run())
    loop.close()
    return result
