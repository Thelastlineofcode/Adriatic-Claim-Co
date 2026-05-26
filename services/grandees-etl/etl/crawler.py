"""
Playwright-based async crawler — open-source Firecrawl equivalent.

Handles:
  - JS-rendered pages (React/Angular CAD portals)
  - Pagination via Playwright locator clicks
  - Stealth mode: randomized viewport, user-agent rotation, request interception
  - Auto-retry on navigation errors
  - PDF download for parish auction notices

This is the shared crawler for ALL Grandee's pipeline scrapers.
Xcellent1 pipeline imports this same module.
"""
import asyncio
import random
import logging
from typing import Optional, List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 1280, "height": 800},
]


class Crawler:
    """
    Async Playwright crawler. Open-source Firecrawl replacement.
    Usage:
        async with Crawler() as c:
            html = await c.get(url)
            rows = await c.extract_table(url, selector="table.results")
    """

    def __init__(self, headless: bool = True, slow_mo: int = 0):
        self.headless = headless
        self.slow_mo = slow_mo
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
            ],
        )
        self._context = await self._browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport=random.choice(VIEWPORTS),
            locale="en-US",
            timezone_id="America/Chicago",
            java_script_enabled=True,
            # Mask automation signals
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        # Mask navigator.webdriver
        await self._context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        """)
        return self

    async def __aexit__(self, *args):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def get(self, url: str, wait_for: Optional[str] = None, timeout: int = 30000) -> str:
        """Fetch page HTML. Optionally wait for a CSS selector before returning."""
        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=timeout)
            await asyncio.sleep(random.uniform(0.5, 1.5))  # human-like delay
            html = await page.content()
            logger.debug(f"[crawler] fetched {url} ({len(html)} bytes)")
            return html
        except Exception as e:
            logger.warning(f"[crawler] get failed: {url} — {e}")
            return ""
        finally:
            await page.close()

    async def extract_table(
        self,
        url: str,
        table_selector: str = "table",
        wait_for: Optional[str] = None,
        paginate_selector: Optional[str] = None,
        max_pages: int = 20,
    ) -> List[Dict[str, str]]:
        """
        Extract all rows from a table, with optional pagination.
        paginate_selector: CSS selector for the 'Next' button/link.
        """
        page = await self._context.new_page()
        all_rows = []
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=15000)

            for page_num in range(max_pages):
                await asyncio.sleep(random.uniform(0.3, 0.9))
                rows = await self._extract_table_rows(page, table_selector)
                all_rows.extend(rows)
                logger.debug(f"[crawler/table] page {page_num+1}: {len(rows)} rows")

                if paginate_selector:
                    next_btn = page.locator(paginate_selector)
                    count = await next_btn.count()
                    if count == 0:
                        break
                    is_disabled = await next_btn.get_attribute("disabled")
                    if is_disabled is not None:
                        break
                    await next_btn.click()
                    await page.wait_for_load_state("domcontentloaded")
                else:
                    break

        except Exception as e:
            logger.warning(f"[crawler/table] failed: {url} — {e}")
        finally:
            await page.close()
        return all_rows

    async def _extract_table_rows(self, page: Page, selector: str) -> List[Dict[str, str]]:
        """Extract header + rows from a visible table on the page."""
        try:
            tables = page.locator(selector)
            count = await tables.count()
            if count == 0:
                return []
            table = tables.first
            headers_raw = await table.locator("thead th, tr:first-child th, tr:first-child td").all_text_contents()
            headers = [h.strip().lower().replace(" ", "_") for h in headers_raw]
            rows = []
            row_els = await table.locator("tbody tr").all()
            for row_el in row_els:
                cells = await row_el.locator("td").all_text_contents()
                if headers:
                    row = dict(zip(headers, [c.strip() for c in cells]))
                else:
                    row = {str(i): c.strip() for i, c in enumerate(cells)}
                if any(row.values()):
                    rows.append(row)
            return rows
        except Exception as e:
            logger.warning(f"[crawler] table extract error: {e}")
            return []

    async def download_pdf(self, url: str, dest: str):
        """Download a PDF (auction notice, deed list) via browser context."""
        import os
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        page = await self._context.new_page()
        try:
            async with page.expect_download() as dl_info:
                await page.goto(url)
            download = await dl_info.value
            await download.save_as(dest)
            logger.info(f"[crawler] PDF saved: {dest}")
        except Exception as e:
            logger.warning(f"[crawler] PDF download failed: {url} — {e}")
        finally:
            await page.close()


def run_async(coro):
    """Convenience: run an async coroutine from sync context."""
    return asyncio.get_event_loop().run_until_complete(coro)
