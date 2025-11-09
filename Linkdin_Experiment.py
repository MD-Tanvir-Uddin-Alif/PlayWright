from playwright.sync_api import sync_playwright

from urllib.parse import urlparse
import time
import json

def get_expiry(cookie):
    for key in ("expiry", "expirationDate", "expires", "expire", "expiration"):
        if key in cookie and cookie[key]:
            try:
                return int(float(cookie[key]))
            except Exception:
                pass
    return None

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded', timeout=40000)

        with open("linkdin_cookies.json", "r", encoding="utf-8") as f:
            cookies = json.load(f)

        current_host = urlparse(page.url).hostname
        added = 0

        for cookie in cookies:
            cookie_payload = {
                "name": cookie.get("name"),
                "value": cookie.get("value", ""),
                "path": cookie.get("path") or "/",
                "domain": cookie.get("domain") or f".{current_host}"
            }

            if "secure" in cookie:
                cookie_payload["secure"] = bool(cookie["secure"])
            if "httpOnly" in cookie:
                cookie_payload["httpOnly"] = bool(cookie["httpOnly"])

            expiry = get_expiry(cookie)
            if expiry:
                cookie_payload["expires"] = expiry

            try:
                context.add_cookies([cookie_payload])
                added += 1
            except Exception as e:
                print(f"Failed to add cookie {cookie.get('name')!r}: {e}. Payload: {cookie_payload}")

        print(f"Attempted to add {len(cookies)} cookies, successfully added {added}.")
        time.sleep(2)
        page.reload()
        time.sleep(5)
        
        
        page.goto()
        browser.close()


if __name__ == '__main__':
    main()
