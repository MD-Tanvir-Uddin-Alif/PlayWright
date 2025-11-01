from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from queue import Queue
import logging
import time


logging.basicConfig(
    filename='Youtube_Comment_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def Scrape_Comments(link):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.goto(link)
        
        

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,slow_mo=6)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto('https://www.youtube.com/', wait_until='domcontentloaded', timeout=50000)
        # logging.info("YOutube Loded sucessfully")
        
        page.locator('input[name="search_query"]').fill("PUBG")
        page.keyboard.press("Enter")
        
        page.wait_for_selector('ytd-video-renderer', timeout=30000)
        for _ in range(3):
            page.evaluate("window.scrollBy(0, window.innerHeight);")
            time.sleep(2)
        
        loded_videos = page.locator('ytd-video-renderer')
        count = loded_videos.count()
        # logging.info("Video Loded Sucessfully")
        
        
        # video_link_queue = Queue()
        for i in range(count):
            video = loded_videos.nth(i)
            video_link = video.locator('a[id="thumbnail"]').get_attribute('href')
            # video_link_queue.put(video_link)
            # logging.info("video link loded sucessfully")
            print('------------------------------------')
            print("https://www.youtube.com"+video_link)
        
        time.sleep(6)
        browser.close()



if __name__ == '__main__':
    main()