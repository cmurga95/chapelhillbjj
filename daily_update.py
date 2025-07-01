
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import re
from io import StringIO

async def login_and_get_csv(email, password, url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        await page.goto(url)

        # --- STEP 1: Enter email ---
        await page.fill('input[type="text"]', email)
        await page.wait_for_timeout(1000)
        print("Email entered")
        # --- STEP 2: Click "Next" ---
        await page.click('button:has-text("Next")')
        print("Next pressed")
        # --- STEP 3: Enter password ---
        await page.fill('input[type="password"]', password)
        print("Filled password")

        # --- STEP 4: Click "Login" ---
        await page.click('button:has-text("Login")')
        print("Login button clicked")
        await page.wait_for_timeout(5000)  # Wait for login to complete
        # --- STEP 6: Navigate to target report page ---
        await page.goto("https://chgjj.pushpress.com/reporting/engagement?tab=Member+Attendance")

        await page.wait_for_selector('iframe[src*="analytics.pushpress.com/"]', timeout=30000)

        print("Iframe found!")

        async def wait_for_frame(page, url_substring, timeout=30000, poll_interval=500):
            max_attempts = timeout // poll_interval
            for _ in range(max_attempts):
                for frame in page.frames:
                    if url_substring in frame.url:
                        return frame
                await asyncio.sleep(poll_interval / 1000)
            raise TimeoutError(f"Frame with URL containing '{url_substring}' not found within {timeout} ms")

        # Usage example:
        frame = await wait_for_frame(page, "analytics.pushpress.com/", timeout=60000)
        print("Frame found:", frame.url)

        try:
            # Wait for the "Check-in Detail" tile to load
            await frame.wait_for_selector('h2:has-text("Check-in Detail")', timeout=5000)
            print("✅ Check-in Detail element found in the frame!")

            # Step 1: Open the "is member" filter dropdown
            await frame.click('span:has-text("is member")')
            await frame.wait_for_timeout(1000)

            # Step 2: Click checkboxes (ensure they're visible first)
            # "member", 
            for label in ["lead", "non-member"]:
                print(f"Looking for exact label: {label}")
                checkbox = frame.locator('label', has_text=re.compile(rf'^{label}$'))
                await checkbox.wait_for(state='visible', timeout=3000)
                await checkbox.click()
                await frame.wait_for_timeout(300)
                print("✅ Checkboxes clicked!")
            await page.keyboard.press("Escape")
            await page.mouse.click(0, 0)  # Click outside to close dropdown
            print("Clicking outside")
            await frame.click('span:has-text("This Month")')
            date_selector = frame.locator('span', has_text = "Last 30 Days")
            await date_selector.wait_for(state='visible', timeout=3000)
            await date_selector.click()
            print("✅ Date range set to Last 30 Days")
            await frame.wait_for_timeout(1000)  # Wait for the date range to apply
            await page.keyboard.press("Escape")
            await page.mouse.click(0, 0)  # Click outside to close dropdown
            print("Clicking outside")
            for i in range(3):
                print(f"Attempt {i+1} to find update button..")
                try:
                    f = frame.wait_for_selector('button:has-text("Update")')
                    await f
                    if f:
                        print("✅ Update button found!")
                        break
                except Exception as e:
                    print("❌ Update button not found, trying to locate it differently:", e)

            # Step 3: Locate and click the Update button
            update_button = frame.locator('button:has-text("Update")')
            await update_button.click(timeout = 15000)
            print("✅ Update button clicked!")
            await frame.wait_for_timeout(1000)  # Wait for any potential updates to complete
            # if not disabled:
                
            #     print("✅ Update button clicked!")
            # else:
            #     print("⚠️ Update button is disabled")

            # Step 4: Locate the correct Tile Actions button under the "Check-in Detail" section
            tile_section = frame.locator('h2:has-text("Check-in Detail")').locator('..').locator('..')  # Go up to tile container
            tile_button = tile_section.locator('button:has(div:has-text("Tile actions"))')
            await tile_button.wait_for(state="visible", timeout=5000)
            print("✅ Tile actions button found!")
            await tile_button.click()
            print("✅ Tile actions button clicked!")
            # Step 5: Click the "Export to CSV" option
            await frame.wait_for_selector('button:has-text("Download Data")', timeout=20000)
            download_button = await frame.query_selector('button:has-text("Download Data")')
            if download_button:
                visible = await download_button.is_visible()
                print("Download Data button visible?", visible)
                await download_button.click()
                print("Download Data button clicked!")
            else:
                print("Download Data button not found")

            # Click the input to open the dropdown menu
            await frame.click('#listbox-input-qr-export-modal-format')  # open dropdown
            await frame.wait_for_timeout(500)  # wait for options to appear
            await frame.click('li[role="option"]:has-text("CSV")')
            print("CSV option selected!")
            # await frame.wait_for_timeout(15000)  # Wait for download to complete
            await page.keyboard.press("Escape")
            
            # Set up waiting for new page
            new_page_promise = context.wait_for_event("page")

            
            # Click the "Open in Browser" button
            await frame.click('#qr-export-modal-open')

            # Wait for the new tab (page) to open
            new_page = await new_page_promise

            print("New page opened:", new_page.url)

            import urllib.parse
            # Parse the URL and modify the query parameters
            new_page_url = new_page.url
            parsed = list(urllib.parse.urlparse(new_page_url))

            query = dict(urllib.parse.parse_qsl(parsed[4]))

            query['limit'] = '1000000'

            parsed[4] = urllib.parse.urlencode(query)
            
            new_url = urllib.parse.urlunparse(parsed)

            await new_page.goto(new_url)

            await new_page.wait_for_load_state()

            csv_text = await new_page.content()

            # Optional: Strip HTML if wrapped

            csv_clean = re.sub(r'<[^>]+>', '', csv_text).strip()

            # print(csv_clean[:1000])  # Print first 1000 characters for debugging
            df = pd.read_csv(StringIO(csv_clean))
            # with open("checkins.csv", "w", encoding="utf-8") as f:
            #     f.write(csv_clean)
            
            return df
    
        except Exception as e:
            print("❌ Error during automation:", e)




            # await frame.wait_for_selector('h2:has-text("Check-in Detail")', timeout=2000)
            # print("Updated element found in the frame!")

        # Close browser and return
        await browser.close()
        # return cookie_dict

if __name__ == "__main__":
    import asyncio
    url = "https://chgjj.pushpress.com/"
    email = "cmmurgav@gmail.com"
    password = "Chapelhillbjj1234."
    
    cookies = asyncio.run(login_and_get_csv(email, password, url))
    print(cookies)