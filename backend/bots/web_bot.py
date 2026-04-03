"""
Playwright-based web bot. Each task type maps to a handler method.
"""
from __future__ import annotations
import asyncio
import json
from typing import Any, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import structlog

from app.config import settings
from app.utils.retry import bot_retry

logger = structlog.get_logger(__name__)


class BotResult:
    def __init__(self, success: bool, data: Any = None, error: str = None, logs: list[str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.logs = logs or []

    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "logs": self.logs,
        }


class WebBot:
    def __init__(
        self,
        headless: bool = True,
        timeout_ms: int = 30000,
        proxy: Optional[str] = None,
        cookies: Optional[str] = None,
    ):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.proxy = proxy
        self.cookies_raw = cookies
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._logs: list[str] = []

    def _log(self, msg: str):
        self._logs.append(msg)
        logger.info(msg)

    async def __aenter__(self):
        await self.launch()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def launch(self):
        self._playwright = await async_playwright().start()
        launch_opts: dict[str, Any] = {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        }
        if self.proxy:
            launch_opts["proxy"] = {"server": self.proxy}

        self._browser = await self._playwright.chromium.launch(**launch_opts)
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        self._context.set_default_timeout(self.timeout_ms)

        if self.cookies_raw:
            try:
                cookies = json.loads(self.cookies_raw)
                await self._context.add_cookies(cookies)
                self._log("Restored session cookies")
            except Exception as e:
                self._log(f"Failed to restore cookies: {e}")

        self._page = await self._context.new_page()
        # Stealth: hide navigator.webdriver
        await self._page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self._log("Browser launched")

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._log("Browser closed")

    async def save_cookies(self) -> str:
        """Persist current session cookies as JSON string."""
        cookies = await self._context.cookies()
        return json.dumps(cookies)

    # ------------------------------------------------------------------ #
    # Task handlers                                                        #
    # ------------------------------------------------------------------ #

    @bot_retry(max_attempts=settings.BOT_MAX_RETRIES)
    async def navigate(self, url: str) -> BotResult:
        self._log(f"Navigating to {url}")
        response = await self._page.goto(url, wait_until="domcontentloaded")
        title = await self._page.title()
        self._log(f"Page title: {title}")
        return BotResult(
            success=True,
            data={"url": self._page.url, "title": title, "status": response.status},
            logs=self._logs,
        )

    @bot_retry(max_attempts=settings.BOT_MAX_RETRIES)
    async def login(self, url: str, username_selector: str, password_selector: str,
                    submit_selector: str, username: str, password: str,
                    success_selector: Optional[str] = None) -> BotResult:
        self._log(f"Logging in at {url}")
        await self._page.goto(url, wait_until="domcontentloaded")
        await self._page.fill(username_selector, username)
        await asyncio.sleep(0.5)
        await self._page.fill(password_selector, password)
        await asyncio.sleep(0.3)
        await self._page.click(submit_selector)

        if success_selector:
            try:
                await self._page.wait_for_selector(success_selector, timeout=10000)
                self._log("Login success (found success_selector)")
            except Exception:
                self._log("Login may have failed — success_selector not found")
                return BotResult(
                    success=False,
                    error="Login verification failed",
                    logs=self._logs,
                )
        else:
            await self._page.wait_for_load_state("networkidle")

        cookies = await self.save_cookies()
        self._log("Login complete, cookies saved")
        return BotResult(
            success=True,
            data={"cookies": cookies, "url": self._page.url},
            logs=self._logs,
        )

    @bot_retry(max_attempts=settings.BOT_MAX_RETRIES)
    async def scrape(self, url: str, selectors: dict[str, str]) -> BotResult:
        """
        selectors: {"field_name": "css_selector", ...}
        Returns a dict of scraped values.
        """
        self._log(f"Scraping {url}")
        await self._page.goto(url, wait_until="domcontentloaded")
        data: dict[str, Any] = {}
        for field, selector in selectors.items():
            try:
                el = await self._page.query_selector(selector)
                data[field] = (await el.inner_text()).strip() if el else None
            except Exception as e:
                data[field] = None
                self._log(f"Scrape field '{field}' failed: {e}")
        return BotResult(success=True, data=data, logs=self._logs)

    @bot_retry(max_attempts=settings.BOT_MAX_RETRIES)
    async def form_fill(self, url: str, fields: list[dict], submit_selector: str) -> BotResult:
        """
        fields: [{"selector": "...", "value": "...", "type": "text|select|checkbox"}, ...]
        """
        self._log(f"Filling form at {url}")
        await self._page.goto(url, wait_until="domcontentloaded")
        for field in fields:
            selector = field["selector"]
            value = field["value"]
            ftype = field.get("type", "text")
            if ftype == "select":
                await self._page.select_option(selector, value)
            elif ftype == "checkbox":
                if value:
                    await self._page.check(selector)
                else:
                    await self._page.uncheck(selector)
            else:
                await self._page.fill(selector, value)
            await asyncio.sleep(0.2)

        await self._page.click(submit_selector)
        await self._page.wait_for_load_state("networkidle")
        return BotResult(
            success=True,
            data={"final_url": self._page.url},
            logs=self._logs,
        )

    @bot_retry(max_attempts=settings.BOT_MAX_RETRIES)
    async def click(self, url: str, selector: str, wait_after_ms: int = 1000) -> BotResult:
        self._log(f"Clicking {selector} on {url}")
        await self._page.goto(url, wait_until="domcontentloaded")
        await self._page.click(selector)
        await asyncio.sleep(wait_after_ms / 1000)
        return BotResult(
            success=True,
            data={"url_after_click": self._page.url},
            logs=self._logs,
        )

    @bot_retry(max_attempts=settings.BOT_MAX_RETRIES)
    async def screenshot(self, url: str, path: str = "/tmp/screenshot.png") -> BotResult:
        await self._page.goto(url, wait_until="networkidle")
        await self._page.screenshot(path=path, full_page=True)
        self._log(f"Screenshot saved to {path}")
        return BotResult(success=True, data={"path": path}, logs=self._logs)

    # ------------------------------------------------------------------ #
    # Dispatcher                                                           #
    # ------------------------------------------------------------------ #

    async def run_task(self, task_type: str, payload: dict) -> BotResult:
        handlers = {
            "navigate": lambda p: self.navigate(p["url"]),
            "login": lambda p: self.login(**p),
            "scrape": lambda p: self.scrape(p["url"], p["selectors"]),
            "form_fill": lambda p: self.form_fill(p["url"], p["fields"], p["submit_selector"]),
            "click": lambda p: self.click(p["url"], p["selector"], p.get("wait_after_ms", 1000)),
            "screenshot": lambda p: self.screenshot(p["url"], p.get("path", "/tmp/screenshot.png")),
        }
        handler = handlers.get(task_type)
        if not handler:
            return BotResult(success=False, error=f"Unknown task type: {task_type}", logs=self._logs)
        try:
            return await handler(payload or {})
        except Exception as e:
            logger.exception("bot.run_task.error", task_type=task_type, error=str(e))
            return BotResult(success=False, error=str(e), logs=self._logs)