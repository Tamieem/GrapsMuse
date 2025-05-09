
import requests
from bs4 import BeautifulSoup
from database.models import Promotion
import re
from datetime import datetime

BASE_URL = "https://www.cagematch.net"
PROMOTIONS_URL = f"{BASE_URL}/?id=8&view=promotions"


def extract_cagematch_id_from_url(url: str):
    match = re.search(r"id=8&nr=(\d+)", url)
    return int(match.group(1)) if match else None


def parse_country_from_location(location: str) -> str:
    return location.split(",")[-1].strip() if "," in location else location.strip()


def parse_founded_years(founded_str: str) -> tuple:
    founded_str = founded_str.replace("–", "-").strip()
    parts = founded_str.split("-")

    try:
        start_year = int(parts[0])
    except ValueError:
        start_year = None

    if len(parts) == 1 or not parts[1].strip():
        end_year = None
        is_active = True
    else:
        try:
            end_year = int(parts[1])
            is_active = False
        except ValueError:
            end_year = None
            is_active = True

    years_active = (datetime.now().year - start_year) if is_active and start_year else \
                   (end_year - start_year) if start_year and end_year else None

    return start_year, end_year, is_active, years_active


def scrape_promotions_list() -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(PROMOTIONS_URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # The correct table has class 'TBase TableBorderColor'
    table = soup.find('table', class_='TBase TableBorderColor')
    if table is None:
        raise ValueError("\u26a0\ufe0f Could not find promotion table. The page structure may have changed or your request was blocked.")

    rows = table.find_all('tr')[1:]  # skip header
    promotions = []

    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 5:
            continue

        link = cells[2].find('a')
        if not link:
            continue

        name = link.text.strip()
        href = link['href']
        cagematch_id = extract_cagematch_id_from_url(href)

        location = cells[3].text.strip()
        country = parse_country_from_location(location)

        founded_str = cells[4].text.strip()
        year_founded, year_disbanded, is_active, years_active = parse_founded_years(founded_str)

        promotions.append({
            "name": name,
            "country": country,
            "year_founded": year_founded,
            "year_disbanded": year_disbanded,
            "is_active": is_active,
            "years_active": years_active,
            "cagematch_id": cagematch_id,
        })

    return promotions

def save_promotions_to_db(promotions: list, session):
    for promo in promotions:
        existing = session.query(Promotion).filter_by(cagematch_id=promo['cagematch_id']).first()
        if existing:
            continue  # Skip duplicates

        promotion = Promotion(
            name=promo['name'],
            country=promo['country'],
            year_founded=promo['year_founded'],
            year_disbanded=promo['year_disbanded'],
            is_active=promo['is_active'],
            years_active=promo['years_active'],
            cagematch_id=promo['cagematch_id']
        )
        session.add(promotion)

    session.commit()
