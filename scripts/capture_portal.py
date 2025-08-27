from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "portal.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto("http://127.0.0.1:8765/?latest=1")
        page.wait_for_timeout(2000)
        page.screenshot(path=out.as_posix(), full_page=True)
        browser.close()
    print(f"Saved screenshot to {out}")


if __name__ == "__main__":
    main()

