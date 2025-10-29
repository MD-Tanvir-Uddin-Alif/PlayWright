from playwright.sync_api import sync_playwright
import time
import csv

csv_file = "flipkart_mobile.csv"

with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Image_Link", "Product_Link", "Price", "Product_Name"])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,slow_mo=5)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto('https://www.flipkart.com', wait_until="domcontentloaded")

        browsName = "mobile"
        for page_num in range(1, 20):
            page.goto(f"https://www.flipkart.com/search?q={browsName}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={page_num}")
            
            # Scroll to load all products
            last_height = page.evaluate("document.body.scrollHeight")
            while True:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            PageProducts = page.locator("div._75nlfW")
            count = PageProducts.count()

            for i in range(count):
                product = PageProducts.nth(i)
                produt_images = product.locator("img")
                image_link = produt_images.nth(0).get_attribute('src')

                product_all_links = product.locator('a')
                product_link = product_all_links.nth(0).get_attribute('href')

                product__all_prices = product.locator("div:has-text('₹')")
                product_price = product__all_prices.nth(-1).inner_text().strip()

                product_title = produt_images.nth(0).get_attribute('alt')

                print(f'-----------------{i}-----------------------------')
                print(image_link)
                print(f'https://www.flipkart.com' + product_link)
                print(product_price)
                print(product_title)

                # Write row to CSV
                writer.writerow([image_link, f'https://www.flipkart.com{product_link}', product_price, product_title])

        time.sleep(5)
        browser.close()
