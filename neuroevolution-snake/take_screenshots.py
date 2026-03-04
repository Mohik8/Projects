"""
Multi-scenario screenshots for the Neuroevolution Snake AI dashboard.
  01_idle_dashboard.png   - fresh dashboard, no training yet
  02_sidebar_controls.png - sidebar showing hyperparameter sliders
  03_mid_training.png     - mid-training with live chart + stat cards
  04_replay_section.png   - replay section with animated board + metrics
"""

import os, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(r"C:\Users\mudit\mohik\Projects\neuroevolution-snake\screenshots")
OUT.mkdir(exist_ok=True)
URL = "http://localhost:8501"


def wait_for_app(page, extra_ms=1500):
    page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=20_000)
    page.wait_for_timeout(extra_ms)


def snap(page, name):
    path = str(OUT / f"{name}.png")
    page.screenshot(path=path, full_page=True)
    print(f"  Saved {path}")


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    # ── 1. Idle dashboard ────────────────────────────────────────────
    print("[1/4] Idle dashboard...")
    page.goto(URL, wait_until="domcontentloaded")
    wait_for_app(page)
    snap(page, "01_idle_dashboard")

    # ── 2. Sidebar open with sliders ─────────────────────────────────
    print("[2/4] Sidebar controls...")
    toggle = page.query_selector("[data-testid='collapsedControl']")
    if toggle:
        toggle.click()
        page.wait_for_timeout(600)
    sidebar = page.query_selector("[data-testid='stSidebar']")
    if sidebar:
        sidebar.evaluate("el => el.scrollTo(0, 240)")
        page.wait_for_timeout(400)
    snap(page, "02_sidebar_controls")

    # ── 3. Mid-training (click Start, wait ~12 s for a few gens) ─────
    print("[3/4] Mid-training...")
    # Re-open sidebar to reach start button area first, then close for chart
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)
    start_btn = page.locator("button:has-text('Start Training')").first
    if not start_btn.is_visible():
        start_btn = page.locator("button:has-text('Start')").first
    start_btn.click()
    print("   Waiting 14 s for a few generations...")
    page.wait_for_timeout(14_000)
    # Collapse sidebar so chart is fully visible
    toggle = page.query_selector("[data-testid='collapsedControl']")
    if toggle:
        toggle.click()
        page.wait_for_timeout(500)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(600)
    snap(page, "03_mid_training")

    # ── 4. Stop + scroll to replay section ───────────────────────────
    print("[4/4] Replay section...")
    stop_btn = page.locator("button:has-text('Stop')").first
    if stop_btn.is_visible():
        stop_btn.click()
        page.wait_for_timeout(2500)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)
    snap(page, "04_replay_section")

    browser.close()

print(f"\nDone. Screenshots saved to: {OUT}")
