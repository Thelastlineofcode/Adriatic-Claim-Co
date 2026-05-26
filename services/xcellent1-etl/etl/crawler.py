"""
Playwright crawler for Xcellent1 ETL.
Shared implementation — see grandees-etl/etl/crawler.py for full docstring.
Kept as a local copy to maintain independent service lifecycle.
"""
import asyncio
import random
import logging
from typing import Optional, List, Dict
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
]


class Crawler:
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
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage"],
        )
        self._context = await self._browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport=random.choice(VIEWPORTS),
            locale="en-US",
            timezone_id="America/Chicago",
            java_script_enabled=True,
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
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
        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=timeout)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            return await page.content()
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
                    if await next_btn.count() == 0:
                        break
                    if await next_btn.get_attribute("disabled") is not None:
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
        try:
            tables = page.locator(selector)
            if await tables.count() == 0:
                return []
            table = tables.first
            headers_raw = await table.locator("thead th, tr:first-child th, tr:first-child td").all_text_contents()
            headers = [h.strip().lower().replace(" ", "_") for h in headers_raw]
            rows = []
            for row_el in await table.locator("tbody tr").all():
                cells = await row_el.locator("td").all_text_contents()
                row = dict(zip(headers, [c.strip() for c in cells])) if headers else {str(i): c.strip() for i, c in enumerate(cells)}
                if any(row.values()):
                    rows.append(row)
            return rows
        except Exception as e:
            logger.warning(f"[crawler] table extract error: {e}")
            return []
