from playwright.sync_api import sync_playwright
import time



def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,slow_mo=6)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto('https://www.youtube.com/', wait_until='domcontentloaded', timeout=50000)
        time.sleep(6)



if __name__ == '__main__':
    main()