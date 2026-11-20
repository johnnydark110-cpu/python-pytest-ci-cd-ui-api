"""Playwright 浏览器生命周期管理。"""

from __future__ import annotations

from types import TracebackType
from typing import Self

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Playwright,
    sync_playwright,
)

DEFAULT_VIEWPORT = {
    "width": 1440,
    "height": 900,
}


class BrowserManager:
    """管理 Playwright 与 Chromium 的会话级生命周期。"""

    def __init__(
        self,
        *,
        headless: bool = True,
        slow_mo: float = 0,
    ) -> None:
        self.headless = headless
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self.slow_mo = slow_mo

    @property
    def browser(self) -> Browser:
        """返回已经启动的 Chromium 浏览器。"""
        if self._browser is None:
            raise RuntimeError("浏览器尚未启动，请先调用 start()")
        return self._browser

    def start(self) -> None:
        """启动Playwright和chromium"""
        if self._browser is not None:
            return

        playwright = sync_playwright().start()

        try:
            browser = playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
            )
        except Exception:
            playwright.stop()
            raise

        self._playwright = playwright
        self._browser = browser

    def new_context(
        self, *, base_url: str, ignore_https_errors: bool = False
    ) -> BrowserContext:
        """创建一条测试独立的浏览器上下文"""
        return self.browser.new_context(
            base_url=base_url,
            ignore_https_errors=ignore_https_errors,
            viewport=DEFAULT_VIEWPORT,
        )

    def close(self) -> None:
        """关闭浏览器和 Playwright，重复调用是安全的。"""
        browser = self._browser
        playwright = self._playwright

        self._browser = None
        self._playwright = None

        if browser is not None:
            browser.close()

        if playwright is not None:
            playwright.stop()

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
