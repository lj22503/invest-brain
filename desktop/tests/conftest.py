# desktop/tests/conftest.py
# Plan 5 任务 6：tauri-driver Playwright e2e 共享 fixture

import pytest
from playwright.sync_api import sync_playwright, Browser


@pytest.fixture(scope="session")
def tauri_app() -> Browser:
    """Connect to tauri-driver (default port 4444).

    前提：CI / 本地已启 tauri-driver + Tauri 应用。
    真正驱动逻辑：tauri_app.new_page() → page.goto("tauri://localhost") → 操作 UI。
    """
    with sync_playwright() as p:
        # tauri-driver 默认监听 4444
        browser = p.chromium.connect_over_cdp("http://localhost:4444")
        yield browser