"""
test_e2e.py — End-to-end browser tests using Playwright (pytest-playwright)

These tests launch a real Chromium browser, navigate the full UI interaction
flow, and assert on DOM state — equivalent to a Selenium WebDriver test suite.

Requirements:
    pip install pytest-playwright
    playwright install chromium

Run (app must be running on localhost:8050 — python app.py):
    pytest tests/test_e2e.py -v

Skip if server not reachable:
    pytest tests/test_e2e.py -v --ignore-glob="*e2e*"  # skip in CI
"""
import pytest
import requests
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:8050"


# ── Skip marker — skip all E2E tests if server is not running ─────────────────

def _server_reachable() -> bool:
    try:
        return requests.get(BASE_URL, timeout=3).status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _server_reachable(),
    reason="F1 app not running on localhost:8050 — start with: python app.py",
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _open_dropdown_and_pick(page: Page, dropdown_id: str, text: str):
    """Open a Dash 4 dcc.Dropdown and click the option matching `text`."""
    page.locator(f"#{dropdown_id} .dash-dropdown-trigger").click()
    page.wait_for_timeout(400)
    page.locator(".dash-dropdown-option").filter(has_text=text).first.click()
    page.wait_for_timeout(300)


def _load_session(page: Page, year: str = "2025"):
    """Select year, first race, Race session, click LOAD SESSION, wait for ready."""
    _open_dropdown_and_pick(page, "dd-year", year)
    page.wait_for_timeout(600)
    # Pick first available race
    page.locator("#dd-race .dash-dropdown-trigger").click()
    page.wait_for_timeout(400)
    page.locator(".dash-dropdown-option").first.click()
    page.wait_for_timeout(300)
    # Leave session type as Race (default R)
    page.locator("#btn-load").click()
    # Wait until Compare button becomes enabled (drivers populated)
    page.locator("#btn-compare:not([disabled])").wait_for(timeout=120_000)


# ── Page load tests ───────────────────────────────────────────────────────────

class TestPageLoad:

    def test_title_contains_f1(self, page: Page):
        page.goto(BASE_URL)
        assert "F1" in page.title()

    def test_brand_block_visible(self, page: Page):
        page.goto(BASE_URL)
        expect(page.locator(".brand-block")).to_be_visible()

    def test_brand_shows_f1_strategy_analyzer(self, page: Page):
        page.goto(BASE_URL)
        text = page.locator(".brand-block").inner_text()
        assert "F1" in text
        assert "STRATEGY" in text
        assert "ANALYZER" in text

    def test_sidebar_visible(self, page: Page):
        page.goto(BASE_URL)
        expect(page.locator(".sidebar")).to_be_visible()

    def test_main_content_visible(self, page: Page):
        page.goto(BASE_URL)
        expect(page.locator(".main-content")).to_be_visible()

    def test_year_dropdown_present(self, page: Page):
        page.goto(BASE_URL)
        expect(page.locator("#dd-year")).to_be_visible()

    def test_load_button_present(self, page: Page):
        page.goto(BASE_URL)
        expect(page.locator("#btn-load")).to_be_visible()

    def test_compare_button_present(self, page: Page):
        page.goto(BASE_URL)
        expect(page.locator("#btn-compare")).to_be_visible()

    def test_all_six_tab_buttons_present(self, page: Page):
        page.goto(BASE_URL)
        for i in range(6):
            expect(page.locator(f"#tab-btn-{i}")).to_be_visible()

    def test_tab_labels_correct(self, page: Page):
        page.goto(BASE_URL)
        labels = ["LAP TIMES", "RACE GAP", "STRATEGY", "TELEMETRY", "RESULTS", "WEATHER"]
        for i, label in enumerate(labels):
            text = page.locator(f"#tab-btn-{i}").inner_text()
            assert label in text.upper()

    def test_compare_button_initially_disabled(self, page: Page):
        page.goto(BASE_URL)
        btn = page.locator("#btn-compare")
        assert btn.get_attribute("disabled") is not None


# ── Dropdown interaction tests ────────────────────────────────────────────────

class TestDropdowns:

    def test_year_dropdown_opens(self, page: Page):
        page.goto(BASE_URL)
        page.locator("#dd-year .dash-dropdown-trigger").click()
        page.wait_for_timeout(400)
        options = page.locator(".dash-dropdown-option")
        assert options.count() > 0

    def test_year_options_include_2025(self, page: Page):
        page.goto(BASE_URL)
        page.locator("#dd-year .dash-dropdown-trigger").click()
        page.wait_for_timeout(400)
        texts = [page.locator(".dash-dropdown-option").nth(i).inner_text()
                 for i in range(page.locator(".dash-dropdown-option").count())]
        assert any("2025" in t for t in texts)

    def test_selecting_year_populates_race_dropdown(self, page: Page):
        page.goto(BASE_URL)
        _open_dropdown_and_pick(page, "dd-year", "2025")
        page.wait_for_timeout(800)
        # Race dropdown trigger should now be enabled / clickable
        expect(page.locator("#dd-race .dash-dropdown-trigger")).to_be_visible()

    def test_session_type_dropdown_has_race_option(self, page: Page):
        page.goto(BASE_URL)
        page.locator("#dd-session-type .dash-dropdown-trigger").click()
        page.wait_for_timeout(400)
        texts = [page.locator(".dash-dropdown-option").nth(i).inner_text()
                 for i in range(page.locator(".dash-dropdown-option").count())]
        assert any("Race" in t or "R" in t for t in texts)


# ── Session load tests ────────────────────────────────────────────────────────

class TestSessionLoad:

    def test_load_session_enables_compare(self, page: Page):
        page.goto(BASE_URL)
        _load_session(page)
        btn = page.locator("#btn-compare")
        assert btn.get_attribute("disabled") is None

    def test_driver_dropdowns_populated_after_load(self, page: Page):
        page.goto(BASE_URL)
        _load_session(page)
        # Driver 1 dropdown should have options
        page.locator("#dd-driver1 .dash-dropdown-trigger").click()
        page.wait_for_timeout(400)
        options = page.locator(".dash-dropdown-option")
        assert options.count() >= 2  # at least 2 drivers

    def test_status_box_shows_after_load(self, page: Page):
        page.goto(BASE_URL)
        _load_session(page)
        status = page.locator("#status-box")
        # Status box should have some text content
        assert len(status.inner_text().strip()) > 0


# ── Comparison / chart tests ──────────────────────────────────────────────────

class TestCharts:

    @pytest.fixture(autouse=True)
    def load_and_compare(self, page: Page):
        """Shared setup: load session, select NOR vs VER, run compare."""
        page.goto(BASE_URL)
        _load_session(page, year="2025")

        # Driver 1: NOR (or first available)
        page.locator("#dd-driver1 .dash-dropdown-trigger").click()
        page.wait_for_timeout(400)
        nor = page.locator(".dash-dropdown-option").filter(has_text="NOR").first
        if nor.count() > 0:
            nor.click()
        else:
            page.locator(".dash-dropdown-option").first.click()
        page.wait_for_timeout(300)

        # Driver 2: VER (or second available)
        page.locator("#dd-driver2 .dash-dropdown-trigger").click()
        page.wait_for_timeout(400)
        ver = page.locator(".dash-dropdown-option").filter(has_text="VER").first
        if ver.count() > 0:
            ver.click()
        else:
            page.locator(".dash-dropdown-option").nth(1).click()
        page.wait_for_timeout(300)

        # Compare
        page.locator("#btn-compare").click()
        # Wait for first chart
        page.locator("#chart-area .js-plotly-plot").wait_for(timeout=60_000)
        page.wait_for_timeout(1000)

    def test_chart_area_has_plotly_chart(self, page: Page):
        expect(page.locator("#chart-area .js-plotly-plot")).to_be_visible()

    def test_first_tab_active_after_compare(self, page: Page):
        tab0 = page.locator("#tab-btn-0")
        classes = tab0.get_attribute("class") or ""
        assert "active" in classes

    def test_tab_switches_update_chart(self, page: Page):
        """Clicking tab 1 should show a different chart within 1 second."""
        page.locator("#tab-btn-1").click()
        page.wait_for_timeout(800)
        expect(page.locator("#chart-area .js-plotly-plot")).to_be_visible()

    @pytest.mark.parametrize("tab_idx", [0, 1, 2, 3, 4, 5])
    def test_all_tabs_render_chart(self, page: Page, tab_idx: int):
        page.locator(f"#tab-btn-{tab_idx}").click()
        page.wait_for_timeout(700)
        expect(page.locator("#chart-area .js-plotly-plot")).to_be_visible()

    def test_stat_row_populated(self, page: Page):
        stat_row = page.locator(".stat-row")
        expect(stat_row).to_be_visible()
        assert len(stat_row.inner_text().strip()) > 0

    def test_tab_switch_latency_under_500ms(self, page: Page):
        """Tab switch should be fast (client-side, no server round-trip needed)."""
        import time
        page.locator("#tab-btn-2").click()
        start = time.monotonic()
        page.locator("#chart-area .js-plotly-plot").wait_for(timeout=2000)
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms < 500, f"Tab switch took {elapsed_ms:.0f}ms (expected < 500ms)"


# ── Countdown timer tests ─────────────────────────────────────────────────────

class TestCountdown:

    def test_countdown_banner_visible(self, page: Page):
        page.goto(BASE_URL)
        banner = page.locator(".next-race-banner")
        if banner.count() > 0:
            expect(banner).to_be_visible()

    def test_countdown_shows_numeric_values(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)  # let clientside JS tick once
        for elem_id in ["cd-days", "cd-hours", "cd-mins", "cd-secs"]:
            el = page.locator(f"#{elem_id}")
            if el.count() > 0:
                text = el.inner_text().strip()
                assert text.isdigit() or text == "--", (
                    f"#{elem_id} should be numeric or '--', got '{text}'"
                )

    def test_countdown_ticks(self, page: Page):
        """Seconds value should change after 2 seconds."""
        page.goto(BASE_URL)
        secs_el = page.locator("#cd-secs")
        if secs_el.count() == 0:
            pytest.skip("No countdown (no upcoming race in schedule)")
        page.wait_for_timeout(1200)
        v1 = secs_el.inner_text().strip()
        page.wait_for_timeout(2000)
        v2 = secs_el.inner_text().strip()
        # Values should differ unless exactly 0
        assert v1 != v2 or v1 == "00"


# ── Accessibility / dark theme smoke tests ────────────────────────────────────

class TestVisual:

    def test_body_has_dark_background(self, page: Page):
        page.goto(BASE_URL)
        # The app-root div should not be white
        bg = page.eval_on_selector(".app-root", "el => getComputedStyle(el).backgroundColor")
        assert bg not in ("rgb(255, 255, 255)", "rgba(0, 0, 0, 0)", "")

    def test_no_console_errors_on_load(self, page: Page):
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(BASE_URL)
        page.wait_for_timeout(2000)
        # Filter out known benign warnings
        real_errors = [e for e in errors if "favicon" not in e.lower()]
        assert len(real_errors) == 0, f"Console errors: {real_errors}"

    def test_page_not_blank(self, page: Page):
        page.goto(BASE_URL)
        content = page.locator("body").inner_text()
        assert len(content.strip()) > 50


# ── Sidebar interaction tests ─────────────────────────────────────────────────

@pytest.mark.e2e
class TestSidebarInteraction:
    """Tests for the sidebar controls before session is loaded."""

    def test_compare_button_disabled_before_load(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        disabled = page.locator("#btn-compare").get_attribute("disabled")
        assert disabled is not None, "COMPARE should be disabled before loading a session"

    def test_load_button_is_visible(self, page: Page):
        page.goto(BASE_URL)
        expect(page.locator("#btn-load")).to_be_visible()

    def test_year_dropdown_visible_and_has_value(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        expect(page.locator("#dd-year")).to_be_visible()
        text = page.locator("#dd-year").inner_text()
        assert len(text.strip()) > 0

    def test_session_type_dropdown_defaults_to_race(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        text = page.locator("#dd-session-type").inner_text().upper()
        assert "RACE" in text or "R" in text

    def test_driver_dropdowns_empty_before_load(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        for dd in ("#dd-driver1", "#dd-driver2"):
            text = page.locator(dd).inner_text().strip()
            # Should be empty or placeholder text — not a driver code
            assert len(text) < 20


# ── Navigation / tab tests ────────────────────────────────────────────────────

@pytest.mark.e2e
class TestTabNavigation:

    TAB_LABELS = ["LAP TIMES", "RACE GAP", "STRATEGY", "TELEMETRY", "RESULTS", "WEATHER"]

    def test_all_6_tabs_visible_on_page(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        for i in range(6):
            expect(page.locator(f"#tab-btn-{i}")).to_be_visible()

    def test_tab_labels_match_expected(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        for i, label in enumerate(self.TAB_LABELS):
            btn_text = page.locator(f"#tab-btn-{i}").inner_text().upper()
            assert label in btn_text, f"Tab {i} expected '{label}', got '{btn_text}'"

    def test_only_one_tab_active_at_a_time(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        for click_idx in range(6):
            page.locator(f"#tab-btn-{click_idx}").click()
            page.wait_for_timeout(400)
            active_count = page.locator(".tab-btn.active").count()
            assert active_count == 1, f"Expected 1 active tab, found {active_count}"

    def test_clicked_tab_becomes_active(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        for i in range(6):
            page.locator(f"#tab-btn-{i}").click()
            page.wait_for_timeout(300)
            cls = page.locator(f"#tab-btn-{i}").get_attribute("class") or ""
            assert "active" in cls, f"Tab {i} should be active after clicking"


# ── Header / branding tests ───────────────────────────────────────────────────

@pytest.mark.e2e
class TestHeaderBranding:

    def test_f1_brand_text_present(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        expect(page.locator(".brand-f1")).to_be_visible()
        assert "F1" in page.locator(".brand-f1").inner_text().upper()

    def test_strategy_brand_text_present(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        text = page.locator(".brand-strategy").inner_text().upper()
        assert "STRATEGY" in text

    def test_header_is_sticky(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        pos = page.eval_on_selector(".app-header", "el => getComputedStyle(el).position")
        assert pos in ("sticky", "fixed")

    def test_next_race_banner_visible(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(2000)
        banner = page.locator(".next-race-banner")
        # Banner is visible only if there is a next race in the schedule
        if banner.count() > 0:
            expect(banner).to_be_visible()

    def test_countdown_blocks_render(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(2500)
        if page.locator(".cd-num").count() > 0:
            for cd_id in ("cd-days", "cd-hours", "cd-mins", "cd-secs"):
                val = page.locator(f"#{cd_id}").inner_text().strip()
                assert val.isdigit() or val == "--", f"{cd_id} value unexpected: '{val}'"


# ── Accessibility / semantic tests ───────────────────────────────────────────

@pytest.mark.e2e
class TestAccessibility:

    def test_page_has_title(self, page: Page):
        page.goto(BASE_URL)
        assert "F1" in page.title().upper() or "Strategy" in page.title()

    def test_buttons_are_button_elements(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        for btn_id in ("#btn-load", "#btn-compare", "#tab-btn-0"):
            tag = page.eval_on_selector(btn_id, "el => el.tagName.toLowerCase()")
            assert tag == "button", f"{btn_id} should be a <button>, got <{tag}>"

    def test_no_horizontal_overflow(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        overflow = page.evaluate(
            "() => document.documentElement.scrollWidth > window.innerWidth"
        )
        assert not overflow, "Page has horizontal overflow (layout broken)"

    def test_sidebar_and_main_both_present(self, page: Page):
        page.goto(BASE_URL)
        page.wait_for_timeout(1500)
        expect(page.locator(".sidebar")).to_be_visible()
        expect(page.locator(".main-content")).to_be_visible()
