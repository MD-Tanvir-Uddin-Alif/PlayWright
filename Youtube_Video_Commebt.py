from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
import time
import logging
import csv
import os

# ----------------- Logging -----------------
logging.basicConfig(
    filename='Youtube_Comment_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ----------------- CSV File -----------------
CSV_FILE = "youtube_comments.csv"

# Ensure CSV exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Video URL", "Comment Number", "Comment Text"])

# ----------------- Async Comment Scraper -----------------
async def Scrape_Comments(link: str):
    logging.info(f"Starting scraping for: {link}")
    print(f"Scraping: {link}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto(link, wait_until='networkidle', timeout=60000)

            for _ in range(10):
                await page.evaluate("window.scrollBy(0, window.innerHeight);")
                await asyncio.sleep(2)

            await page.wait_for_selector('//div[@id="comment-container"]', timeout=50000)
            all_comments = page.locator('xpath=//div[@id="comment-container"]')
            count = await all_comments.count()
            logging.info(f"Found {count} comments for video: {link}")

            for i in range(count):
                comment = all_comments.nth(i)
                spans = comment.locator("yt-attributed-string#content-text span")
                span_count = await spans.count()

                parts = []
                for j in range(span_count):
                    text = await spans.nth(j).text_content()
                    if text:
                        parts.append(text)

                full_comment = " ".join(parts).strip()

                with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([link, i + 1, full_comment])

                logging.info(f"Video: {link} | Comment {i+1}: {full_comment}")

        except Exception as e:
            logging.error(f"Failed to scrape {link}: {e}")
            print(f"Error scraping {link}: {e}")

        await browser.close()
        logging.info(f"Finished scraping for: {link}")
        print(f"Finished: {link}")

# ----------------- Run Scraper in Batches -----------------
async def Run_All_Scraper(links, batch=5):
    total_links = len(links)
    logging.info(f"Total videos found: {total_links}")
    for i in range(0, total_links, batch):
        batch_links = links[i:i + batch]
        logging.info(f"Processing batch {i//batch + 1}: {batch_links}")
        print(f"\nProcessing batch {i//batch + 1}: {batch_links}")
        await asyncio.gather(*(Scrape_Comments(link) for link in batch_links))

# ----------------- Main Function -----------------
def main():
    links = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=6)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto('https://www.youtube.com/', wait_until='domcontentloaded', timeout=50000)

        page.locator('input[name="search_query"]').fill("iphone 17")
        page.keyboard.press("Enter")

        page.wait_for_selector('ytd-video-renderer', timeout=30000)
        for _ in range(3):
            page.evaluate("window.scrollBy(0, window.innerHeight);")
            time.sleep(2)

        loaded_videos = page.locator('ytd-video-renderer')
        count = loaded_videos.count()

        for i in range(count):
            video = loaded_videos.nth(i)
            video_link = video.locator('a[id="thumbnail"]').get_attribute('href')
            if video_link:
                links.append("https://www.youtube.com" + video_link)

        browser.close()

    asyncio.run(Run_All_Scraper(links, batch=5))

if __name__ == '__main__':
    main()
