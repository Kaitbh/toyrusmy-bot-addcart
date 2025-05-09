import time
import subprocess
import os
import argparse
from playwright.sync_api import sync_playwright

# File containing product URLs (one URL per line)
URL_LIST_FILE = "product_urls.txt"

# Create product_urls.txt if it does not exist
if not os.path.exists(URL_LIST_FILE):
    with open(URL_LIST_FILE, "w") as f:
        f.write("# Add one product URL per line below\n")
    print(
        f"Created '{URL_LIST_FILE}'. Please add product URLs to this file before running the script."
    )

# Interval (in seconds) between stock checks
CHECK_INTERVAL_SECONDS = 15

# Flag to control manual login
MANUAL_LOGIN = True  # Set to True to login manually, False for automated login

# Path to Playwright storage state file
STORAGE_STATE_PATH = "auth_state.json"

# Parse command line arguments for sender email, receiver email, and refresh time
parser = argparse.ArgumentParser()
parser.add_argument(
    "--sender",
    type=str,
    required=True,
    help="Sender email address for AppleScript Mail",
)
parser.add_argument(
    "--receiver",
    type=str,
    required=True,
    help="Receiver email address for AppleScript Mail",
)
parser.add_argument(
    "--refresh-time", type=int, help="Interval in seconds between stock checks"
)
args = parser.parse_args()
SENDER_EMAIL = args.sender
RECEIVER_EMAIL = args.receiver
if args.refresh_time:
    CHECK_INTERVAL_SECONDS = args.refresh_time

with sync_playwright() as p:  # Launch Playwright and open a browser [oai_citation:3‡playwright.dev](https://playwright.dev/python/docs/library#:~:text=from%20playwright)
    browser = p.chromium.launch(
        headless=False  # Set to False for visual mode
    )  # Launch Chromium browser in headed (visual) mode

    # Use persistent authentication if session file exists
    if os.path.exists(STORAGE_STATE_PATH):
        context = browser.new_context(storage_state=STORAGE_STATE_PATH)
        print("Loaded existing authentication session.")
        login_page = context.new_page()
        login_page.goto("https://www.toysrus.com.my/")
    else:
        context = browser.new_context()
        login_page = context.new_page()
        login_page.goto("https://www.toysrus.com.my/login/")
        print(
            "No saved session found. Please log in manually in the opened browser window."
        )
        input("Press Enter after you have successfully logged in...")
        # Save session after manual login
        context.storage_state(path=STORAGE_STATE_PATH)
        print(f"Session saved to {STORAGE_STATE_PATH}")

    # 3. Read product URLs from file
    try:
        with open(URL_LIST_FILE, "r") as f:
            product_urls = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
    except FileNotFoundError:
        print(f"Error: URL list file '{URL_LIST_FILE}' not found.")
        browser.close()
        exit(1)

    if not product_urls:
        print(f"No product URLs specified in '{URL_LIST_FILE}'. Exiting.")
        browser.close()
        exit(0)

    # Open each product page and prepare for monitoring
    pages_to_monitor = []  # list of tuples (page, url) for active pages
    for url in product_urls:
        try:
            page = context.new_page()
            response = page.goto(url)
        except Exception as e:
            print(f"Failed to load {url}: {e}")
            page.close()
            continue
        # Check HTTP response status
        if response is None or response.status >= 400:
            print(
                f"Skipping {url} (invalid URL or page error, status {response.status if response else 'N/A'})."
            )
            page.close()
        else:
            pages_to_monitor.append((page, url))
            print(f"Monitoring product page: {url}")

    if not pages_to_monitor:
        print("No valid product pages to monitor. Exiting.")
        browser.close()
        exit(0)

    # 4. Monitor each page for "Add to Cart" availability
    items_to_add = set(url for _, url in pages_to_monitor)
    items_added = set()

    while items_to_add - items_added:
        for page, url in list(pages_to_monitor):
            if url in items_added:
                continue
            # Look for the "Add to Cart" button on the page
            add_button = page.query_selector("text=Add to Cart")
            if add_button:
                try:
                    add_button.click()  # Add the item to cart
                    print(f"Item available! Added to cart: {url}")
                    # 5. Trigger email notification via AppleScript
                    apple_script = (
                        'tell application "Mail"\n'
                        f'set newMessage to make new outgoing message with properties {{subject:"ToysRUs Stock Alert", content:"The product {url} is now in stock and has been added to your cart.", visible:false}} \n'
                        f'set sender of newMessage to "{SENDER_EMAIL}"\n'
                        "tell newMessage\n"
                        f'make new to recipient at end of to recipients with properties {{address:"{RECEIVER_EMAIL}"}}\n'
                        "send\n"
                        "end tell\n"
                        "end tell"
                    )
                    try:
                        subprocess.run(["osascript", "-e", apple_script], check=True)
                        print("Notification email sent via AppleScript.")
                    except Exception as e:
                        print(f"Failed to send AppleScript email notification: {e}")
                    items_added.add(url)
                    page.close()  # Close the tab after adding to cart
                    pages_to_monitor.remove((page, url))
                except Exception as e:
                    print(f"Error clicking 'Add to Cart' for {url}: {e}")
        if items_to_add == items_added:
            break  # All items added to cart
        # If not all items found in this cycle, refresh each page and check again after 15 seconds
        for page, url in pages_to_monitor:
            if url not in items_added:
                page.reload()
        print(
            f"No stock yet for some items. Checking again in {CHECK_INTERVAL_SECONDS} seconds..."
        )
        time.sleep(CHECK_INTERVAL_SECONDS)

    # 6. Cleanup: close browser (Playwright will also auto-close on exiting the 'with' block)
    browser.close()
    print(
        "Script terminated after all items were added to cart and notifications sent."
    )
