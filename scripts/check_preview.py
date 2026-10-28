#!/usr/bin/env python3
"""Optional Chromium integration check; needs playwright and system chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def check():
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / "dist"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path="/usr/bin/chromium", headless=True,
                                        args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page(viewport={"width": 1600, "height": 1300})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.server_port}/specimen.html")
            page.evaluate("document.fonts.ready")
            assert page.evaluate("document.fonts.check('100px Neon')")
            assert page.evaluate("[...document.fonts].find(f=>f.family==='Neon').status") == "loaded"
            page.screenshot(path=str(ROOT / "dist/preview.png"), full_page=True)
            page.locator(".hero").screenshot(path=str(ROOT / "dist/title.png"))
            page.locator("#sample").fill("ČĆĐŠŽ čćđšž 210GB")
            assert page.locator("#output").inner_text() == "ČĆĐŠŽ čćđšž 210GB"
            page.locator("#size").focus()
            page.keyboard.press("End")
            assert page.locator("#output").evaluate("e=>getComputedStyle(e).fontSize") == "130px"
            page.locator("#mode").click()
            page.evaluate("document.fonts.ready")
            assert page.locator("#mode").get_attribute("aria-pressed") == "true"
            assert page.evaluate("[...document.fonts].find(f=>f.family==='Mono').status") == "loaded"
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert not errors, errors
            browser.close()
            print("PASS: color font, Mono font, Croatian sample, size control, toggle, mobile layout")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    check()
