from playwright.sync_api import sync_playwright
import time


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=5)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    page.goto('https://www.youtube.com/', wait_until="domcontentloaded", timeout=30000)
    
    page.locator('input[name="search_query"]').fill("PUBG")
    page.keyboard.press("Enter")

    page.wait_for_selector('ytd-video-renderer', timeout=30000)

    page.evaluate("window.scrollBy(0, window.innerHeight);")
    time.sleep(2) 

    loded_videos = page.locator('ytd-video-renderer')
    count = loded_videos.count()
    
    for i in range(count):
        video = loded_videos.nth(i)
        
        video_link = video.locator('a[id="thumbnail"]').get_attribute('href')
        video_title = video.locator('a[id="video-title"]').get_attribute('title')
        chanel_link = video.locator('a[id="channel-thumbnail"]').get_attribute('href')
        
        
        print(f'---------------------------{i}----------------------------------')
        print("https://www.youtube.com"+video_link)
        print(video_title)
        print("https://www.youtube.com"+chanel_link)

    browser.close()
