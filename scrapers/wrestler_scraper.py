# scrapers/wrestler_scraper.py

import requests
from bs4 import BeautifulSoup
from utils.parsers import parse_height, parse_weight, parse_years_active
from database.db_utils import get_or_create_promotion
from database.models import Wrestler
from datetime import datetime


def scrape_wrestler_profile(url: str) -> dict:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    info_table = soup.select_one('table.InformationBox')
    data = {
        'name': None,
        'real_name': None,
        'promotion': None,
        'height': None,
        'weight': None,
        'debut': None,
        'is_active': True,
        'years_active': None,
        'retirement': None
    }

    for row in info_table.select('tr'):
        th = row.find('th')
        td = row.find('td')
        if not th or not td:
            continue

        label = th.get_text(strip=True)
        value = td.get_text(strip=True)

        if 'Name' in label and not data['name']:
            data['name'] = value
        elif 'Real Name' in label:
            data['real_name'] = value
        elif 'Promotion' in label:
            data['promotion'] = value
        elif 'Height' in label:
            data['height'] = parse_height(value)
        elif 'Weight' in label:
            data['weight'] = parse_weight(value)
        elif 'Debut' in label:
            try:
                data['debut'] = datetime.strptime(value, "%B %d, %Y")
            except:
                data['debut'] = None
        elif 'In Ring Experience' in label:
            data['years_active'] = parse_years_active(value)
        elif 'End of In-ring Career' in label:
            data['retirement'] = datetime.strptime(value, "%B %d, %Y")
            data['is_active'] = False

    return data


def save_wrestler_to_db(data: dict, session):
    # Optional: handle promotion as a foreign key
    promotion_id = None
    if data['promotion']:
        promotion = get_or_create_promotion(session, data['promotion'])
        promotion_id = promotion.id

    wrestler = Wrestler(
        name=data['name'],
        real_name=data['real_name'],
        promotion_id=promotion_id,
        height=data['height'],
        weight=data['weight'],
        debut=data['debut'],
        is_active=data['is_active'],
        years_active=data['years_active'],
        retirement=data['retirement']
    )
    session.add(wrestler)
    session.commit()
    return wrestler
