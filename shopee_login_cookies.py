from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=5)

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    page = context.new_page()
    page.goto("https://shopee.sg/", wait_until="domcontentloaded")

    # Wait for email field to appear (avoids errors)
    page.wait_for_selector('//input[@type="text" or @name="loginKey"]', timeout=10000)

    email = "mdtanviruddin36@gmail.com"
    password = "Shopee2345"

    # Fill login fields
    email_field = page.locator('//*[@id="main"]/div/div[2]/div/div[2]/div/div/div/div[2]/div/div[2]/form/div[1]/div[1]/input')
    password_field = page.locator('//*[@id="main"]/div/div[2]/div/div[2]/div/div/div/div[2]/div/div[2]/form/div[2]/div[1]/input')

    email_field.fill(email)
    password_field.fill(password)

    password_field.press("Enter")


    # Wait for page to fully load (network idle = no pending requests)
    page.wait_for_load_state("networkidle")
    time.sleep(10)  # give Shopee extra time to set cookies

    # ✅ Get and save cookies
    cookies = page.context.cookies()
    cookies_json = json.dumps(cookies, indent=4)

    with open("shopee_cookies.json", "w", encoding="utf-8") as f:
        f.write(cookies_json)

    print("✅ Cookies saved successfully to shopee_cookies.txt")

    browser.close()
