import os, time
from playwright.sync_api import sync_playwright

out = r"C:\Users\mudit\mohik\Projects\neuroevolution-snake\screenshots"
os.makedirs(out, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto("http://localhost:8501", wait_until="networkidle")
    time.sleep(4)
    # Full dashboard screenshot
    page.screenshot(path=os.path.join(out, "dashboard.png"), full_page=True)
    print("dashboard.png saved")
    browser.close()

print("Done")
