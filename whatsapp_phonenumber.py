from playwright.sync_api import sync_playwright
import time
import csv

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=5)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    page = context.new_page()
    page.goto("https://web.whatsapp.com/")

    # Wait for main container
    page.wait_for_selector("div#app", timeout=60000)
    print("Please scan the QR code within 30 seconds...")
    time.sleep(30)

    # Wait for chat list
    page.wait_for_selector("#pane-side", timeout=30000)
    pane = page.locator("#pane-side")

    contacts_data = {}
    previous_height = 0
    scroll_increment = 300   # pixels per scroll
    max_scrolls = 100        # adjust depending on number of contacts

    for i in range(max_scrolls):
        # Extract current contacts
        all_contacts = page.locator("span[dir='auto']")
        count = all_contacts.count()

        for j in range(count):
            try:
                contact = all_contacts.nth(j)
                title = contact.get_attribute("title")
                if title and title not in contacts_data:
                    contacts_data[title] = {'title': title}
            except:
                pass
        
        print(f"Scroll {i+1}: {len(contacts_data)} unique contacts collected.")

        # Scroll little by little
        pane.evaluate(f"el => el.scrollTop += {scroll_increment}")
        time.sleep(4.5)  # allow time for next batch of contacts to load

        # Stop if no new contacts appear after scrolling
        current_height = pane.evaluate("el => el.scrollTop")
        if current_height == previous_height:
            print("Reached bottom (no more contacts loading).")
            break
        previous_height = current_height

    # Save contacts to CSV
    filename = "ContactList.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Index", "Title"])
        for idx, (title, data) in enumerate(contacts_data.items(), 1):
            writer.writerow([idx, data['title']])
            print(f"{idx}. {data['title']}")

    print(f"\n✅ Total {len(contacts_data)} contacts saved to {filename}")
    browser.close()
