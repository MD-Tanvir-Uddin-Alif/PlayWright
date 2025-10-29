from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,slow_mo=5)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.goto('https://www.flipkart.com/')
    
    try:
        page.locator("span:has-text('✕')").click()
    except:
        print("PopUp didnot arrive")
        
    
    page.wait_for_selector("input[name='q']")
    
    page.locator("input[name='q']").fill("laptops")
    page.keyboard.press("Enter")
    
    
    time.sleep(5)
    browser.close()