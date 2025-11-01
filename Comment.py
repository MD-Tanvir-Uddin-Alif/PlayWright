from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False ,slow_mo=3)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.goto("https://www.youtube.com/watch?v=XaoRWJW0VnQ&pp=ygUEUFVCRw%3D%3D")
    
    for i in range(10):
        page.evaluate("window.scrollBy(0, window.innerHeight);")
        page.wait_for_timeout(2000)

    page.wait_for_selector('ytd-comment-thread-renderer', timeout=30000)

    all_comments = page.locator('yt-attributed-string[id=content-text]')
    count = all_comments.count()

    for i in range(count):
        comment = all_comments.nth(i).inner_text()
        print(f'-------------------------{i}------------------------------')
        print(comment)

    page.wait_for_timeout(5000)
    browser.close()
