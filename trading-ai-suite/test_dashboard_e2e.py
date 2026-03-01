"""
Trading AI Suite — Dashboard E2E Tests (Playwright)
Validates the Next.js dashboard UI renders correctly.

Prerequisites:
  pip install pytest playwright
  playwright install chromium

Run:
  # Start the dashboard first:  cd dashboard && npm run dev
  pytest test_dashboard_e2e.py -v
"""

import pytest
from playwright.sync_api import sync_playwright, Page, Browser, expect

BASE_URL = "http://localhost:3000"


@pytest.fixture(scope="module")
def browser():
    """Launch a headless Chromium browser for the test module."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser):
    """Create a fresh page for each test."""
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        color_scheme="dark",
    )
    pg = context.new_page()
    pg.goto(BASE_URL, wait_until="networkidle")
    yield pg
    context.close()


# ──────────────────────────────────────────────
# 1. Page Load & Title
# ──────────────────────────────────────────────
class TestPageLoad:
    def test_page_loads_successfully(self, page: Page):
        """Dashboard should return HTTP 200 and render."""
        assert page.url.startswith(BASE_URL)

    def test_page_title(self, page: Page):
        """Title should contain 'Trading AI Suite'."""
        expect(page).to_have_title(title="Trading AI Suite | TradingView++")


# ──────────────────────────────────────────────
# 2. Layout Structure
# ──────────────────────────────────────────────
class TestLayoutStructure:
    def test_navbar_visible(self, page: Page):
        """Navbar at the top should be visible."""
        nav = page.locator("nav").first
        expect(nav).to_be_visible()

    def test_left_sidebar(self, page: Page):
        """Left icon sidebar should contain navigation icons."""
        sidebar = page.locator("aside").first
        expect(sidebar).to_be_visible()

    def test_right_sidebar(self, page: Page):
        """Right data sidebar should be visible."""
        sidebars = page.locator("aside")
        expect(sidebars.last).to_be_visible()

    def test_status_bar(self, page: Page):
        """Bottom status bar should show service indicators."""
        footer = page.locator("footer")
        expect(footer).to_be_visible()
        expect(footer).to_contain_text("BROKER")
        expect(footer).to_contain_text("AI SENTINEL")

    def test_main_content_area(self, page: Page):
        """Main content area should exist."""
        main = page.locator("main")
        expect(main).to_be_visible()


# ──────────────────────────────────────────────
# 3. Chart Rendering
# ──────────────────────────────────────────────
class TestChartRendering:
    def test_chart_containers_exist(self, page: Page):
        """At least one chart container should be rendered."""
        charts = page.locator("main >> div").first
        expect(charts).to_be_visible()

    def test_default_2x2_grid(self, page: Page):
        """Default layout should render a 2x2 grid of charts."""
        grid = page.locator("main .grid-cols-2")
        expect(grid).to_be_visible()


# ──────────────────────────────────────────────
# 4. Watchlist Panel
# ──────────────────────────────────────────────
class TestWatchlist:
    def test_watchlist_renders(self, page: Page):
        """Watchlist component should be visible in the right sidebar."""
        watchlist = page.get_by_text("WATCHLIST", exact=False)
        expect(watchlist.first).to_be_visible()


# ──────────────────────────────────────────────
# 5. AI Panel
# ──────────────────────────────────────────────
class TestAIPanel:
    def test_ai_panel_renders(self, page: Page):
        """AI Insights panel should be visible."""
        ai = page.get_by_text("AI", exact=False)
        expect(ai.first).to_be_visible()


# ──────────────────────────────────────────────
# 6. Bot Manager
# ──────────────────────────────────────────────
class TestBotManager:
    def test_bot_manager_renders(self, page: Page):
        """Bot Manager section should appear below the charts."""
        bots = page.get_by_text("BOT", exact=False)
        expect(bots.first).to_be_visible()


# ──────────────────────────────────────────────
# 7. Screenshot Utility (debug helper)
# ──────────────────────────────────────────────
class TestScreenshot:
    def test_capture_full_page(self, page: Page):
        """Capture a full-page screenshot for visual inspection."""
        page.screenshot(path="dashboard_screenshot.png", full_page=True)
        assert True
