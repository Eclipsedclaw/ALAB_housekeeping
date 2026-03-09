from playwright.sync_api import sync_playwright
import os
import time
from datetime import datetime


def make_screenshot(output="grafana.png", url=None, password=None, user=None):
    GRAFANA_URL = url or os.getenv("GRAFANA_URL")
    USER = user or os.getenv("GRAFANA_USER")
    PASSWORD = password or os.getenv("GRAFANA_PASSWD")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 3000})
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        page.goto(GRAFANA_URL)
        page.wait_for_timeout(2000)
        page.fill('input[name="user"]', USER)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')
        page.click("button[id=dock-menu-button]")
        time.sleep(10)
        page.evaluate(f"""
        () => {{
            const el = document.createElement('div');
            el.textContent = 'Captured at: {ts} JST';
             el.style.position = 'fixed';
            el.style.top = '16px';
            el.style.left = '50%';
            el.style.transform = 'translateX(-50%)';

            el.style.padding = '10px 24px';
            el.style.background = 'rgba(0, 0, 0, 0.65)';
            el.style.color = 'white';
            el.style.fontSize = '28px';
            el.style.fontWeight = 'bold';
            el.style.fontFamily = 'monospace';

            el.style.borderRadius = '6px';
            el.style.zIndex = 99999;
            el.style.pointerEvents = 'none';  // クリック邪魔しない
            document.body.appendChild(el);
        }}
    """)
        page.screenshot(path=output, full_page=True)
        browser.close()
