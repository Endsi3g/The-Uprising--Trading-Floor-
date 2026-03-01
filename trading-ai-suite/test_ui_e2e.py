"""
Trading AI Suite — UI E2E Tests (Playwright)
Validates that the dashboard UI elements are correctly rendered.
"""

import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:3000"

@pytest.fixture(scope="module")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        try:
            page.goto(BASE_URL, wait_until="networkidle")
        except:
            pytest.skip("Dashboard server not reachable at http://localhost:3000")
        yield page
        browser.close()

def test_dashboard_title(page):
    expect(page).to_have_title("Trading AI Suite | TradingView++")

def test_navigation_elements(page):
    expect(page.locator("nav")).to_be_visible()
    expect(page.locator("aside").first).to_be_visible()

def test_charts_rendering(page):
    # Check if at least one chart container exists
    expect(page.locator("div[id^='chart_']").first).to_be_visible()

def test_sidebars(page):
    # Watchlist and AI Panels
    expect(page.get_by_text("WATCHLIST", exact=False).first).to_be_visible()
    expect(page.get_by_text("AI", exact=False).first).to_be_visible()

def test_bot_manager(page):
    expect(page.get_by_text("BOT", exact=False).first).to_be_visible()

def test_status_bar(page):
    expect(page.locator("footer")).to_be_visible()
    expect(page.locator("footer")).to_contain_text("BROKER")
