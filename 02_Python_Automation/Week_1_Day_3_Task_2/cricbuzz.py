
from playwright.sync_api import sync_playwright, TimeoutError
from pathlib import Path

# Browser settings
HEADLESS = False

LIVE_URL = "https://www.cricbuzz.com/cricket-match/live-scores"

# Save screenshot in the same folder as this Python file
SCREENSHOT_PATH = Path(__file__).resolve().parent / "score.png"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=HEADLESS)

    page = browser.new_page(
        viewport={"width": 1500, "height": 1000},
        device_scale_factor=1
    )

    try:
        print("Opening Cricbuzz Live Scores...")

        # Step 1: Open Cricbuzz
        page.goto(
            LIVE_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Step 2: Allow the webpage to load
        page.wait_for_timeout(8000)

        # Step 3: Display page title
        print("Page Title:", page.title())

        # Step 4: Capture the complete visible webpage
        page.screenshot(
            path=str(SCREENSHOT_PATH),
            full_page=False
        )

        print("\nLive Cricket Score screenshot captured!")
        print("Image saved at:", SCREENSHOT_PATH)

    except TimeoutError:
        print("Cricbuzz took too long to load.")

    except Exception as error:
        print("Error:", error)

    finally:
        browser.close()
        print("Browser closed.")