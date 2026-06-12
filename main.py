import os
import json
import re
import time
import random
from bs4 import BeautifulSoup
from botasaurus.browser import browser, Driver

os.makedirs("output", exist_ok=True)

MIN_PROPERTIES = 200
SLEEP_MIN = 3.0
SLEEP_MAX = 8.0

links = [
    "https://www.inmuebles24.com/locales-comerciales-en-renta.html",
    "https://www.inmuebles24.com/locales-comerciales-en-venta.html",
    "https://www.inmuebles24.com/terrenos-en-venta.html",
]

def page_url(base_url, page):
    if page == 1:
        return base_url
    return base_url.replace(".html", f"-pagina-{page}.html")

def extract_id(url):
    match = re.search(r"-(\d+)\.html", url)
    return match.group(1) if match else None

def parse_card(card):
    layout = card.find(attrs={"data-id": True})
    if not layout:
        return None, {}

    posting_id = layout.get("data-id")

    def qa_text(name):
        el = card.find(attrs={"data-qa": name})
        return el.get_text(" ", strip=True) if el else None

    features_el = card.find(attrs={"data-qa": "POSTING_CARD_FEATURES"})
    features = (
        [s.get_text(strip=True) for s in features_el.find_all("span") if s.get_text(strip=True)]
        if features_el else []
    )

    publisher_el = card.find(attrs={"data-qa": "POSTING_CARD_PUBLISHER"})
    publisher_logo = publisher_el.get("src") if publisher_el and publisher_el.name == "img" else None

    return posting_id, {
        "posting_type": layout.get("data-posting-type"),
        "price": qa_text("POSTING_CARD_PRICE"),
        "features": features,
        "location": qa_text("POSTING_CARD_LOCATION"),
        "publisher_logo": publisher_logo,
    }

def parse_properties(html, url=""):
    soup = BeautifulSoup(html, "html.parser")

    cards_by_id = {}
    for card in soup.find_all(class_="postingsList-module__card-container"):
        posting_id, card_data = parse_card(card)
        if posting_id:
            cards_by_id[posting_id] = card_data

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if "mainEntity" not in data:
                continue
            transaction_type = "rent" if "renta" in url else "sale"
            for item in data["mainEntity"]:
                item_id = extract_id(item.get("url", ""))
                if item_id and item_id in cards_by_id:
                    item.update(cards_by_id[item_id])
                item.pop("contentLocation", None)
                item["transaction_type"] = transaction_type
            return data["mainEntity"]
        except (json.JSONDecodeError, TypeError):
            continue

    return []

@browser(reuse_driver=True, headless=True)
def scrape(driver: Driver, base_url):
    filename = base_url.split("/")[-1].replace(".html", "")
    all_properties = []
    seen_ids = set()
    page = 1

    while len(all_properties) < MIN_PROPERTIES:
        url = page_url(base_url, page)
        print(f"[{filename}] Page {page} — {url}")
        driver.get(url)
        driver.long_random_sleep()
        driver.scroll_to_bottom()
        driver.short_random_sleep()
        html = driver.page_html

        page_props = parse_properties(html, base_url)
        if not page_props:
            print(f"[{filename}] No properties found on page {page}, stopping.")
            break

        new = [p for p in page_props if extract_id(p.get("url", "")) not in seen_ids]
        if not new:
            print(f"[{filename}] No new properties on page {page}, stopping.")
            break

        for p in new:
            seen_ids.add(extract_id(p.get("url", "")))
        all_properties.extend(new)

        print(f"[{filename}] Total so far: {len(all_properties)}")

        if len(all_properties) >= MIN_PROPERTIES:
            break

        delay = random.uniform(SLEEP_MIN, SLEEP_MAX)
        print(f"[{filename}] Sleeping {delay:.1f}s before next page...")
        time.sleep(delay)
        page += 1

    with open(f"output/{filename}.json", "w", encoding="utf-8") as f:
        json.dump(all_properties, f, ensure_ascii=False, indent=2)

    print(f"[{filename}] Saved {len(all_properties)} properties.")
    return all_properties

if __name__ == "__main__":
    scrape(links)
