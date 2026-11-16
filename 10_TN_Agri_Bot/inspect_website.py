
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.tn.gov.in/scheme_list.php?dep_id=Mg=="

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)
print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

print("\n--- SCHEME LINKS FOUND ON THE PAGE ---")

for link in soup.find_all("a", href=True):
    name = link.get_text(" ", strip=True)
    href = urljoin(url, link["href"])

    if name:
        print(f"{name} --> {href}")
