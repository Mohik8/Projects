"""
Multi-scenario screenshots for the Neuroevolution Snake AI dashboard.
"""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(r"C:\Users\mudit\mohik\Projects\neuroevolution-snake\screenshots")
OUT.mkdir(exist_ok=True)
URL = "http://localhost:8501"


def wait_for_content(page):
    """Wait until Streamlit has actually rendered visible text content."""
    # Wait for the title h1 to appear and be visible
    page.wait_for_selector("h1", state="visible", timeout=30_000)
    # Wait for the stats strip or any markdown content
    page.wait_for_selector("[data-testid='stMarkdownContainer']", state="visible", timeout=15_000)
    # Extra settle time for full render
    page.wait_for_timeout(2500)


def snap(page, name):
    path = str(OUT / f"{name}.png")
    page.screenshot(path=path, full_page=True)
    size = os.path.getsize(path)
    print(f"  Saved {name}.png  ({size:,} bytes)")
    if size < 50_000:
        print("  WARNING: file looks suspiciously small — page may not have rendered")


with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )

    # ── 1. Idle dashboard (full page, sidebar visible) ────────────────
    print("[1/4] Idle dashboard...")
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    wait_for_content(page)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)
    snap(page, "01_idle_dashboard")
    ctx.close()

    # ── 2. Sidebar controls (close-up of sidebar element) ─────────────
    print("[2/4] Sidebar controls...")
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    wait_for_content(page)
    # Scroll sidebar down to show mutation + training sliders
    page.evaluate("""
        const inner = document.querySelector('[data-testid="stSidebar"] section');
        if (inner) inner.scrollTop = 280;
    """)
    page.wait_for_timeout(600)
    # Screenshot just the sidebar element
    sidebar_el = page.locator("[data-testid='stSidebar']").first
    path = str(OUT / "02_sidebar_controls.png")
    sidebar_el.screenshot(path=path)
    size = os.path.getsize(path)
    print(f"  Saved 02_sidebar_controls.png  ({size:,} bytes)")
    ctx.close()

    # ── 3. Mid-training ───────────────────────────────────────────────
    print("[3/4] Mid-training...")
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    wait_for_content(page)
    start_btn = page.locator("button:has-text('Start Training')").first
    if not start_btn.is_visible():
        start_btn = page.locator("button:has-text('Start')").first
    start_btn.click()
    print("   Waiting 16 s for generations to run...")
    page.wait_for_timeout(16_000)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(600)
    snap(page, "03_mid_training")
    ctx.close()

    # ── 4. Replay section ─────────────────────────────────────────────
    print("[4/4] Replay section...")
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    wait_for_content(page)
    start_btn = page.locator("button:has-text('Start Training')").first
    if not start_btn.is_visible():
        start_btn = page.locator("button:has-text('Start')").first
    start_btn.click()
    page.wait_for_timeout(10_000)
    stop_btn = page.locator("button:has-text('Stop')").first
    if stop_btn.is_visible():
        stop_btn.click()
        page.wait_for_timeout(3000)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)
    snap(page, "04_replay_section")
    ctx.close()

    browser.close()

print(f"\nDone. Screenshots in: {OUT}")
