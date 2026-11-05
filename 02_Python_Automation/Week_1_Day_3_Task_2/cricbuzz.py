
from playwright.sync_api import sync_playwright, TimeoutError
import re

# First run: False (headed)
# Second run: True (headless)
HEADLESS = False

LIVE_URL = "https://www.cricbuzz.com/cricket-match/live-scores"
RECENT_URL = "https://www.cricbuzz.com/cricket-match/live-scores/recent-matches"

# Match links identified from the Cricbuzz page structure
MATCH_SELECTOR = 'a[href*="/live-cricket-scores/"]'

# Cricket score pattern: 143-5, 185 (40.2), 272 & 142
SCORE_PATTERN = re.compile(
    r"\b\d{1,3}(?:-\d{1,2})?"
    r"(?:\s*&\s*\d{1,3}(?:-\d{1,2})?)?"
    r"(?:\s*\(\d{1,2}(?:\.\d)?\))?\b"
)

# Text that indicates a match is in progress
LIVE_PATTERN = re.compile(
    r"\b(live|innings break|need \d+ runs?|"
    r"trail(?:ing)? by|lead(?:ing)? by|"
    r"opt to bat|opt to bowl|day \d+|"
    r"session|lunch|tea|stumps|"
    r"rain stops play|bad light|target \d+)\b",
    re.IGNORECASE
)

# Text indicating that a match has finished
RESULT_PATTERN = re.compile(
    r"\b(won by|match drawn|drawn|abandoned|"
    r"no result|tied|cancelled)\b",
    re.IGNORECASE
)


def find_match_card(page):
    """Find the first match card containing score information."""

    links = page.locator(MATCH_SELECTOR)

    for i in range(links.count()):
        link = links.nth(i)

        try:
            text = link.inner_text().strip()

            # Check the parent too, as score details may be
            # displayed beside the match link.
            parent = link.locator("xpath=..")
            parent_text = parent.inner_text().strip()

            if len(parent_text) > len(text) and len(parent_text) < 1500:
                text = parent_text
                card = parent
            else:
                card = link

            if SCORE_PATTERN.search(text):
                return card, text

        except Exception:
            continue

    return None, None


with sync_playwright() as p:

    browser = p.chromium.launch(headless=HEADLESS)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})

    try:
        # STEP 1: Check live matches
        print("Opening Cricbuzz live scores...")

        page.goto(LIVE_URL, wait_until="domcontentloaded")

        try:
            page.locator(MATCH_SELECTOR).first.wait_for(
                state="visible",
                timeout=30000
            )
        except TimeoutError:
            pass

        live_card = None
        live_text = None

        live_links = page.locator(MATCH_SELECTOR)

        # STEP 2: Identify a live match
        for i in range(live_links.count()):

            link = live_links.nth(i)

            try:
                text = link.inner_text().strip()
                parent = link.locator("xpath=..")
                parent_text = parent.inner_text().strip()

                if len(parent_text) > len(text) and len(parent_text) < 1500:
                    text = parent_text
                    card = parent
                else:
                    card = link

                has_score = SCORE_PATTERN.search(text)
                is_live = LIVE_PATTERN.search(text)
                is_finished = RESULT_PATTERN.search(text)

                if has_score and is_live and not is_finished:
                    live_card = card
                    live_text = text
                    break

            except Exception:
                continue

        # STEP 3: If live match exists
        if live_card:

            print("\nLIVE MATCH FOUND!")
            print("------------------------------")
            print(live_text)

            live_card.screenshot(path="score.png")

            print("\nLive scoreboard saved as score.png")

        # STEP 4: If no live match, get recent score
        else:

            print("\nThere are no live matches happening right now.")
            print("Fetching the most recent match score...")

            page.goto(RECENT_URL, wait_until="domcontentloaded")

            page.locator(MATCH_SELECTOR).first.wait_for(
                state="visible",
                timeout=30000
            )

            recent_card, recent_text = find_match_card(page)

            if recent_card:

                print("\nMOST RECENT MATCH SCORE")
                print("------------------------------")
                print(recent_text)

                recent_card.screenshot(path="score.png")

                print("\nRecent match scoreboard saved as score.png")

            else:

                print("No recent match score could be located.")
                page.screenshot(path="score.png", full_page=True)
                print("Page screenshot saved as score.png")

    except TimeoutError:
        print("\nCricbuzz did not load the match information in time.")

    except Exception as error:
        print("\nError:", error)

    finally:
        browser.close()
        print("\nBrowser closed.")
