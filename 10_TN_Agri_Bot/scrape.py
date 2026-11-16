
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

BASE_URL = "https://www.tn.gov.in/scheme_list.php?dep_id=Mg=="

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

os.makedirs("data", exist_ok=True)

session = requests.Session()
session.headers.update(HEADERS)

print("Connecting to Tamil Nadu Government website...")

response = session.get(BASE_URL, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Collect individual scheme detail links
schemes = {}

for link in soup.find_all("a", href=True):
    href = link["href"].strip()
    title = link.get_text(" ", strip=True)

    if "scheme_details.php" in href and title:
        detail_url = urljoin(BASE_URL, href)
        schemes[detail_url] = title

print("Total unique scheme pages found:", len(schemes))

all_scheme_data = []

# Visit each scheme detail page
for index, (url, title) in enumerate(schemes.items(), start=1):

    try:
        print(f"\nFetching {index}/{len(schemes)}: {title}")

        detail_response = session.get(url, timeout=30)
        detail_response.raise_for_status()

        detail_soup = BeautifulSoup(
            detail_response.text,
            "html.parser"
        )

        # Remove unnecessary page elements
        for element in detail_soup(
            ["script", "style", "nav", "footer", "header"]
        ):
            element.decompose()

        # Extract main content
        main_content = detail_soup.find("main")

        if not main_content:
            main_content = detail_soup.find(id="main")

        if not main_content:
            main_content = detail_soup.body

        if main_content:
            details = main_content.get_text(
                separator="\n",
                strip=True
            )
        else:
            details = detail_soup.get_text(
                separator="\n",
                strip=True
            )

        if details:
            record = (
                f"SCHEME TITLE: {title}\n"
                f"SOURCE: {url}\n"
                f"SCHEME DETAILS:\n{details}\n"
                + "=" * 70
            )

            all_scheme_data.append(record)
            print("Details extracted successfully.")

        else:
            print("No content found for this page.")

        time.sleep(0.5)

    except requests.RequestException as error:
        print("Failed to fetch:", title, error)

# Save all extracted scheme details
output_file = "data/schemes.txt"

with open(output_file, "w", encoding="utf-8") as file:
    file.write("\n\n".join(all_scheme_data))

print("\n--------------------------------")
print("WEBSITE SCRAPING COMPLETED")
print("Scheme pages found:", len(schemes))
print("Scheme pages extracted:", len(all_scheme_data))
print("Saved to:", output_file)
print("--------------------------------")