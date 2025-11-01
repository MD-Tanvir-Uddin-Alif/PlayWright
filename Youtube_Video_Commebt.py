from playwright.sync_api import sync_playwright
import 
import time



def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,slow_mo=6)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto('https://www.youtube.com/', wait_until='domcontentloaded', timeout=50000)
        
        page.locator('input[name="search_query"]').fill("PUBG")
        page.keyboard.press("Enter")
        
        page.wait_for_selector('ytd-video-renderer', timeout=30000)
        page.evaluate("window.scrollBy(0, window.innerHeight);")
        time.sleep()
        
        time.sleep(6)
        browser.close()



if __name__ == '__main__':
    main()