"""
take_screenshots.py
Headless Playwright script — loads the Dash app, selects 2025 R1 Australia Race,
NOR vs VER, then screenshots every tab plus a banner shot.
"""

import asyncio, os, time
from playwright.async_api import async_playwright

URL  = "http://localhost:8050"
OUT  = os.path.join(os.path.dirname(__file__), "screenshots")
W, H = 1400, 860

TABS = [
    ("tab-btn-0", "lap-times.png"),
    ("tab-btn-1", "race-gap.png"),
    ("tab-btn-2", "strategy.png"),
    ("tab-btn-3", "telemetry.png"),
    ("tab-btn-4", "results.png"),
    ("tab-btn-5", "weather.png"),
]

async def dash_select(page, dropdown_id: str, value: str):
    """Click a Dash 4 dcc.Dropdown and pick the option matching `value`."""
    # Open the dropdown
    trigger = page.locator(f"#{dropdown_id} .dash-dropdown-trigger")
    await trigger.click()
    await page.wait_for_timeout(400)
    # Options are label elements with class dash-dropdown-option
    # They may be inside or outside the dropdown container (portal)
    option = page.locator(".dash-dropdown-option").filter(has_text=value).first
    await option.click()
    await page.wait_for_timeout(300)


async def main():
    os.makedirs(OUT, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx     = await browser.new_context(viewport={"width": W, "height": H})
        page    = await ctx.new_page()

        print("Opening app...")
        await page.goto(URL, timeout=30000)
        await page.wait_for_timeout(2000)

        # ── Select 2025 ───────────────────────────────────────────────────────
        print("Selecting year 2025...")
        await dash_select(page, "dd-year", "2025")
        await page.wait_for_timeout(800)

        # ── Select Race round (wait for races to populate) ────────────────────
        print("Selecting Australia GP...")
        await page.wait_for_selector("#dd-race .dash-dropdown-trigger", timeout=10000)
        # Open menu and pick first option (Round 1 — Australia)
        await page.locator("#dd-race .dash-dropdown-trigger").click()
        await page.wait_for_timeout(500)
        first_option = page.locator(".dash-dropdown-option").first
        race_text    = await first_option.inner_text()
        print(f"  -> picking: {race_text.strip()}")
        await first_option.click()
        await page.wait_for_timeout(300)

        # ── Session type already Race (R) — leave as-is ───────────────────────

        # ── Click LOAD SESSION ────────────────────────────────────────────────
        print("Loading session (may take ~30s for first load)...")
        await page.locator("#btn-load").click()

        # Wait until COMPARE button is enabled (drivers populated)
        await page.locator("#btn-compare:not([disabled])").wait_for(timeout=120000)
        print("Session loaded.")

        # ── Select drivers ────────────────────────────────────────────────────
        print("Selecting drivers...")
        # Driver 1 — try NOR, fallback to first option
        await page.locator("#dd-driver1 .dash-dropdown-trigger").click()
        await page.wait_for_timeout(400)
        nor = page.locator(".dash-dropdown-option").filter(has_text="NOR").first
        if await nor.count() > 0:
            await nor.click()
        else:
            await page.locator(".dash-dropdown-option").first.click()
        await page.wait_for_timeout(300)

        # Driver 2 — try VER, fallback to second option
        await page.locator("#dd-driver2 .dash-dropdown-trigger").click()
        await page.wait_for_timeout(400)
        ver = page.locator(".dash-dropdown-option").filter(has_text="VER").first
        if await ver.count() > 0:
            await ver.click()
        else:
            await page.locator(".dash-dropdown-option").nth(1).click()
        await page.wait_for_timeout(300)

        # ── Take banner screenshot (full page before comparing) ───────────────
        print("Taking banner screenshot...")
        await page.screenshot(path=os.path.join(OUT, "banner.png"), full_page=False)

        # ── Click COMPARE ─────────────────────────────────────────────────────
        print("Running comparison...")
        await page.locator("#btn-compare").click()

        # Wait for chart-area to have content (first chart loaded)
        await page.wait_for_selector("#chart-area .js-plotly-plot", timeout=60000)
        await page.wait_for_timeout(1500)  # let animations settle

        # ── Screenshot each tab ───────────────────────────────────────────────
        for btn_id, filename in TABS:
            print(f"  Screenshotting {filename}...")
            await page.locator(f"#{btn_id}").click()
            await page.wait_for_timeout(700)
            await page.screenshot(
                path=os.path.join(OUT, filename),
                full_page=False,
                clip={"x": 0, "y": 0, "width": W, "height": H},
            )

        await browser.close()

    print("\nDone! Screenshots saved to:", OUT)
    for _, f in TABS:
        print(f"  {f}")
    print("  banner.png")


if __name__ == "__main__":
    asyncio.run(main())
