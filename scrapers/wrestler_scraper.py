
import requests
from bs4 import BeautifulSoup
from database.models import Wrestler
from database.db_utils import get_or_create_promotion
from utils.parsers import parse_height, parse_weight, parse_years_active, parse_date
import re

BASE_URL = "https://www.cagematch.net"
WORKERS_LIST_URL = f"{BASE_URL}/?id=2&view=workers"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


def get_top_wrestlers():
    response = requests.get(WORKERS_LIST_URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="TBase")
    rows = table.find_all("tr")[1:]  # Skip header row

    wrestler_links = []
    for row in rows[:100]:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        link = cells[1].find("a")
        if link and "href" in link.attrs:
            full_url = BASE_URL + "/" + link["href"].lstrip("/")
            wrestler_links.append(full_url)

    return wrestler_links


def get_title_stats(wrestler_id):
    titles_url = f"{BASE_URL}/?id=2&nr={wrestler_id}&page=11"
    response = requests.get(titles_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    titles_won = 0
    title_reigns = 0
    is_champion = False

    captions = soup.find_all("div", class_="Caption")
    for caption in captions:
        heading = caption.get_text(strip=True)

        if "Title Reigns" in heading:
            table = caption.find_next("table", class_="TBase")
            if not table:
                continue
            rows = table.find_all("tr")[1:]  # skip header
            title_reigns = len(rows)

            for row in rows:
                cells = row.find_all("td")
                if len(cells) > 0:
                    timeframe = cells[0].get_text(strip=True).lower()
                    if "today" in timeframe:
                        is_champion = True

        elif "Titles" in heading:
            table = caption.find_next("table", class_="TBase")
            if not table:
                continue
            rows = table.find_all("tr")[1:]  # skip header
            titles_won = len(rows)

    return titles_won, title_reigns, is_champion


def extract_cagematch_id(url: str):
    match = re.search(r"id=2&nr=(\d+)", url)
    return int(match.group(1)) if match else None


def scrape_wrestler_profile(url: str, session):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    # Extract all information boxes
    info_boxes = soup.find_all('div', class_='InformationBoxTable')

    # Flatten all rows from each section
    info_rows = []
    for box in info_boxes:
        info_rows.extend(box.find_all('div', class_='InformationBoxRow'))

    data = {
        'name': None,
        'promotion': None,
        'height_cm': None,
        'weight_kg': None,
        'age': None,
        'debut': None,
        'is_active': True,
        'years_active': None,
        'retirement_date': None,
        'cagematch_id': extract_cagematch_id(url),
        'title_reigns': 0,
        'titles_won': 0,
        'is_champion': False
    }

    for row in info_rows:
        label = row.find('div', class_='InformationBoxTitle')
        value = row.find('div', class_='InformationBoxContents')
        if not label or not value:
            continue
        label = label.get_text(strip=True)
        value = value.get_text(strip=True)

        if 'Current gimmick' in label and not data['name']:
            data['name'] = value
        elif 'Promotion' in label:
            data['promotion'] = value
        elif 'Height' in label:
            data['height_cm'] = parse_height(value)
        elif 'Weight' in label:
            data['weight_kg'] = parse_weight(value)
        elif 'Age' in label:
            data['age'] = int(value.split()[0])  # Extract only the number
        elif 'Beginning of in-ring career' in label:
            data['debut'] = parse_date(value)
        elif 'In-ring experience' in label:
            data['years_active'] = parse_years_active(value)
        elif 'End of in-ring career' in label:
            data['retirement_date'] = parse_date(value)
            data['is_active'] = False

    # Fallback if name is still missing (e.g., retired wrestlers)
    if not data['name']:
        header_box = soup.find("div", class_="HeaderBox")
        if header_box:
            h1 = header_box.find("h1", class_="TextHeader")
            if h1:
                data['name'] = h1.get_text(strip=True)

    titles_won, title_reigns, is_champion = get_title_stats(data['cagematch_id'])
    data['titles_won'] = titles_won
    data['title_reigns'] = title_reigns
    data['is_champion'] = is_champion

    # Check for duplicate by name
    existing = session.query(Wrestler).filter_by(name=data['name']).first()
    if existing:
        print(f"⚠️ Skipping duplicate wrestler: {data['name']}")
        return existing

    promotion_id = None
    if data['promotion']:
        promotion = get_or_create_promotion(session, data['promotion'])
        promotion_id = promotion.id

    wrestler = Wrestler(
        name=data['name'],
        promotion_id=promotion_id,
        height_cm=data['height_cm'],
        weight_kg=data['weight_kg'],
        age=data['age'],
        debut=data['debut'],
        is_active=data['is_active'],
        years_active=data['years_active'],
        retirement_date=data['retirement_date'],
        cagematch_id=data['cagematch_id'],
        title_reigns=data['title_reigns'],
        titles_won=data['titles_won'],
        is_champion=data['is_champion']
    )
    session.add(wrestler)
    session.commit()
    return wrestler


def scrape_top_100_wrestlers(session):
    links = get_top_wrestlers()
    for link in links:
        try:
            print(f"📦 Processing {link}...")
            scrape_wrestler_profile(link, session)
        except Exception as e:
            import traceback
            print(f"❌ Failed to process {link}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {e}")
            print("Traceback:")
            traceback.print_exc()