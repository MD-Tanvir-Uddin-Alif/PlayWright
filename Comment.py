from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False ,slow_mo=3)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.goto("https://www.youtube.com/watch?v=idEAABFzpfg")
    
    for i in range(10):
        page.evaluate("window.scrollBy(0, window.innerHeight);")
        page.wait_for_timeout(2000)


    page.wait_for_selector('//div[@id="comment-container"]', timeout=50000)

    # all_comments = page.locator('yt-attributed-string[id=content-text]')
    all_comments = page.locator('xpath=//div[@id="comment-container"]')
    count = all_comments.count()

    for i in range(count):
        comment = all_comments.nth(i)
        spans = comment.locator("yt-attributed-string#content-text span")
        span_count = spans.count()
        
        parts = []
        for j in range(span_count):
            parts.append(spans.nth(j).text_content())
            
        full_comment = " ".join(parts).strip()
        print(f'-------------------------{i}------------------------------')
        print(full_comment)

    page.wait_for_timeout(5000)
    browser.close()
