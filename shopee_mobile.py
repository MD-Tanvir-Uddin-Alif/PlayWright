import json
import time
import random
import logging
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

from behavior_function import simulate_human_behavior  

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='mobile_shopeee.log',
    filemode='a'
)

load_dotenv()
email = os.getenv('shoppy_mail')
password = os.getenv('shoppy_password')

# --- Utility function to normalize expiry ---
def get_expiry(cookie):
    for key in ("expiry", "expirationDate", "expires", "expire", "expiration"):
        if key in cookie and cookie[key]:
            try:
                return int(float(cookie[key]))
            except Exception:
                pass
    return None


def main():
    # Example stealth User-Agent (realistic)
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.5993.90 Safari/537.36"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        # Create context with extra stealthy options
        context = browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="Asia/Dhaka",   # change if you prefer UTC
            ignore_https_errors=True,
            java_script_enabled=True,
        )

        # Additional init scripts to reduce fingerprinting
        # - hide navigator.webdriver
        # - set navigator.languages
        # - add plugins length
        context.add_init_script(
            """
            // navigator.webdriver removal
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

            // mock languages
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});

            // mock plugins
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});

            // mock permissions.query to avoid detection
            const origQuery = window.navigator.permissions && window.navigator.permissions.query;
            if (origQuery) {
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        origQuery(parameters)
                );
            }
            """ 
        )

        page = context.new_page()

        # Intercept network responses for Shopee API
        api_requests = []

        def capture_response(response):
            """Capture Shopee API JSON responses in readable format"""
            try:
                if "shopee.sg/api/v4/search/search_items" in response.url:
                    try:
                        # Try parsing JSON body directly
                        body_text = response.text()
                        try:
                            json_data = json.loads(body_text)
                        except Exception:
                            json_data = {"raw_text": body_text}

                        entry = {
                            "url": response.url,
                            "status_code": response.status,
                            "response": json_data
                        }

                        # Append to memory list
                        api_requests.append(entry)
                        logging.info(f"Captured API: {response.url}")

                        # Save pretty JSON (readable like website)
                        with open("api_responses.jsonl", "a", encoding="utf-8") as f:
                            json.dump(entry, f, ensure_ascii=False, indent=4)
                            f.write("\n\n")  # spacing between responses

                    except Exception as e:
                        logging.error(f"Error reading body for {response.url}: {e}")

            except Exception as e:
                logging.error(f"Error in capture_response for {getattr(response, 'url', 'unknown')}: {e}")


        # Listen on responses
        context.on("response", capture_response)

        site_url = "https://shopee.sg"
        logging.info(f"Opening {site_url}")
        page.goto(site_url, wait_until="networkidle")

        # Load cookies from file
        with open("shopee_seller.json", "r", encoding="utf-8") as f:
            cookies = json.load(f)

        current_host = urlparse(page.url).hostname
        valid_cookies = []

        for cookie in cookies:
            cookie_payload = {
                "name": cookie.get("name"),
                "value": cookie.get("value", ""),
                "path": cookie.get("path", "/"),
            }

            if "secure" in cookie:
                cookie_payload["secure"] = bool(cookie["secure"])
            if "httpOnly" in cookie:
                cookie_payload["httpOnly"] = bool(cookie["httpOnly"])

            expiry = get_expiry(cookie)
            if expiry:
                # Playwright expects 'expires' as int seconds since epoch
                cookie_payload["expires"] = expiry

            domain = cookie.get("domain")
            if domain:
                normalized = domain.lstrip(".")
                if normalized == current_host:
                    cookie_payload["domain"] = normalized
                else:
                    # skip cookies for other domains
                    continue

            valid_cookies.append(cookie_payload)

        if valid_cookies:
            context.add_cookies(valid_cookies)
            logging.info(f"Added {len(valid_cookies)} cookies.")
        else:
            logging.warning("No valid cookies added to the context.")

        page.reload(wait_until="networkidle")
        time.sleep(4)

        # Try closing popup (same xpath as before)
        try:
            page.locator('xpath=//*[@id="HomePagePopupBannerSection"]/div[2]/div').click(timeout=3000)
        except Exception:
            print("No popup found")

        # Simulate human behaviour (your function supports Playwright page.evaluate)
        simulate_human_behavior(page, random.randint(1, 7))

        # Visit category page (same as your Selenium code)
        page_url = "https://shopee.sg/abc-cat.11000001.11001566?page=0&sortBy=sales"
        logging.info(f"Opening category page: {page_url}")
        page.goto(page_url, wait_until="networkidle")

        # Scroll to trigger lazy-loaded API calls
        print("Scrolling to trigger API calls...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 4);")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        page.evaluate("window.scrollTo(0, 0);")
        time.sleep(2)

        simulate_human_behavior(page, random.randint(1, 7))
        time.sleep(5)  # allow API calls to finish

        # Debug info: if no API requests were captured, print first few requests
        if not api_requests:
            print("⚠️ WARNING: No API requests captured for 'search_items'.")
            print(f"Total network requests: {len(context.requests)}")
            # show the first 20 requests to help debugging
            for req in context.requests[:20]:
                try:
                    print(" -", req.url)
                except Exception:
                    pass

        context.close()
        browser.close()

        print(f"Saved {len(api_requests)} API responses to api_responses.jsonl")


if __name__ == "__main__":
    main()
