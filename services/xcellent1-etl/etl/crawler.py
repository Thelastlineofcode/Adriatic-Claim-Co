# Shared Playwright crawler — same implementation as grandees-etl/etl/crawler.py
# Kept as a local copy to maintain independent service lifecycle.
# If both services are deployed together, consider extracting to a shared lib.
from services.grandees_etl.etl.crawler import Crawler, run_async, USER_AGENTS, VIEWPORTS

__all__ = ["Crawler", "run_async", "USER_AGENTS", "VIEWPORTS"]
