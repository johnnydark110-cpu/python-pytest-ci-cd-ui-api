from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import (
    Locator,
    Page,
    Response,
    expect,
)

DEFAULT_TIMEOUT_MS = 5_000
DEFAULT_SCREENSHOT_DIR = Path(__file__).resolve().parents[1] / "screenshots"
_INVALID_FILENAME_CHARS = re.compile(r"[^0-9A-Za-z_-]+")


class BasePage:
    """封装导航、等待、交互和截图等通用页面能力。"""

    def __init__(
        self,
        page: Page,
        *,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        screenshot_dir: str | Path = DEFAULT_SCREENSHOT_DIR,
    ) -> None:
        self.page = page
        self.timeout_ms = timeout_ms
        self.screenshot_dir = Path(screenshot_dir)

    def goto(self, path: str = "/") -> Response | None:
        """打开相对当前环境 base_url 的页面。"""
        response = self.page.goto(path, wait_until="domcontentloaded")

        expect(self.page.locator("body")).to_be_visible(timeout=self.timeout_ms)
        return response

    def by_test_id(self, test_id: str) -> Locator:
        """按稳定的 data-testid 属性定位元素。"""
        return self.page.get_by_test_id(test_id)

    def wait_for_visible(self, test_id: str) -> Locator:
        """显式等待元素可见并返回 locator。"""
        locator = self.by_test_id(test_id)
        expect(locator).to_be_visible(timeout=self.timeout_ms)
        return locator

    def click(self, test_id: str) -> None:
        """等待元素可见且可用后点击。"""
        locator = self.by_test_id(test_id)

        expect(locator).to_be_visible(timeout=self.timeout_ms)
        expect(locator).to_be_enabled(timeout=self.timeout_ms)
        locator.click(timeout=self.timeout_ms)

    def fill(self, test_id: str, value: str) -> None:
        """等待输入元素可见且可编辑后填写。"""
        locator = self.by_test_id(test_id)

        expect(locator).to_be_visible(timeout=self.timeout_ms)
        expect(locator).to_be_editable(timeout=self.timeout_ms)
        locator.fill(value, timeout=self.timeout_ms)

    def text(self, test_id: str) -> str:
        """等待元素可见并返回去除首尾空白的文本。"""
        return self.wait_for_visible(test_id).inner_text().strip()

    def screenshot(
        self,
        name: str,
        *,
        full_page: bool = True,
    ) -> Path:
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        safe_name = _INVALID_FILENAME_CHARS.sub("_", name).strip("_")
        if not safe_name:
            safe_name = "screenshot"

        screenshot_path = self.screenshot_dir / f"{safe_name}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=full_page)
        return screenshot_path

    def select_option(self, test_id: str, value: str) -> None:
        locator = self.by_test_id(test_id)

        expect(locator).to_be_visible(timeout=self.timeout_ms)
        expect(locator).to_be_enabled(timeout=self.timeout_ms)

        locator.select_option(
            value=value,
            timeout=self.timeout_ms,
        )
