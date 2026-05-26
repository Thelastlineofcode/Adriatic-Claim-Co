"""
MLS comp enrichment via Playwright — HAR.com (Houston MLS).
Adds ARV estimate, days-on-market, recent sales comps to candidate records.

HAR.com is JS-rendered — Playwright required.
"""
import logging
import asyncio
from typing import List, Dict
from etl.crawler import Crawler

logger = logging.getLogger(__name__)


async def _get_har_comps(address: str, zip_code: str) -> Dict:
    """Search HAR.com for comparable sales near an address."""
    query = f"{address} {zip_code} Houston TX".replace(" ", "+")
    url = f"https://www.har.com/search/dosearch?zipcode={zip_code}&q={query}"
    async with Crawler() as c:
        rows = await c.extract_table(
            url,
            table_selector=".search-results table, table.listings",
            wait_for=".search-results, .listing-card, table",
            max_pages=1,
        )
    if not rows:
        return {}
    comps = []
    for row in rows[:5]:
        price_str = row.get("list_price", row.get("price", row.get("sold_price", "0")))
        price = float(price_str.replace("$", "").replace(",", "") or 0)
        if price > 0:
            comps.append(price)
    if comps:
        arv = sum(comps) / len(comps)
        return {"arv_estimate": arv, "comp_count": len(comps), "comp_source": "har.com"}
    return {}


def enrich_with_comps(candidates: List[Dict]) -> List[Dict]:
    """Enrich candidate records with HAR.com comps. Runs async batch."""
    async def _batch():
        tasks = []
        for r in candidates:
            addr = r.get("address", "")
            zip_code = r.get("zip", r.get("zip_code", ""))
            if addr:
                tasks.append(_get_har_comps(addr, zip_code))
            else:
                tasks.append(asyncio.coroutine(lambda: {})())
        return await asyncio.gather(*tasks, return_exceptions=True)

    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(_batch())
    loop.close()

    enriched = []
    for r, comp_data in zip(candidates, results):
        if isinstance(comp_data, dict):
            r.update(comp_data)
        enriched.append(r)
    logger.info(f"[xcellent1/comps] enriched {len(enriched)} records")
    return enriched
