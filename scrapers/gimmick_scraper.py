
import requests
from bs4 import BeautifulSoup
from utils.parsers import parse_date
from database.models import Gimmick
from database.db_utils import get_or_create_promotion
from database.models import Wrestler
import re
from datetime import datetime

BASE_URL = "https://www.cagematch.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


def extract_cagematch_id_from_url(url: str) -> int:
    match = re.search(r"id=2&nr=(\d+)", url)
    return int(match.group(1)) if match else None


def get_gimmick_match_dates(match_history_url: str) -> dict:
    def get_last_page_url(soup):
        pager = soup.select_one("div.NavigationPart")
        if not pager:
            return match_history_url
        last_link = pager.find_all("a", href=True)[-1]
        return BASE_URL + "/" + last_link['href'].lstrip("/")

    def extract_dates_and_promotions(soup):
        """Return list of (date, promotion_name) pairs from a match listing table"""
        results = []
        rows = soup.select("table.TBase.TableBorderColor tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 3:
                date_text = cells[1].get_text(strip=True)
                date = parse_date(date_text)

                promo_link = cells[2].find("a")
                promo_img = promo_link.find("img") if promo_link else None
                promo_name = promo_img["title"].strip() if promo_img and promo_img.has_attr("title") else None

                if date:
                    results.append((date, promo_name))
        return results

    # First page
    r1 = requests.get(match_history_url, headers=HEADERS)
    s1 = BeautifulSoup(r1.content, "html.parser")
    first_page_results = extract_dates_and_promotions(s1)

    last_seen = first_page_results[0][0] if first_page_results else None

    # Last page
    last_page_url = get_last_page_url(s1)
    if last_page_url == match_history_url:
        date_created = first_page_results[-1][0] if first_page_results else None
        promo_name = first_page_results[-1][1] if first_page_results else None
    else:
        r2 = requests.get(last_page_url, headers=HEADERS)
        s2 = BeautifulSoup(r2.content, "html.parser")
        last_page_results = extract_dates_and_promotions(s2)
        date_created = last_page_results[-1][0] if last_page_results else None
        promo_name = last_page_results[-1][1] if last_page_results else None

    return {
        "date_created": date_created,
        "last_seen": last_seen,
        "debut_promotion_name": promo_name
    }


def scrape_gimmicks_for_wrestler(wrestler_id: int, cagematch_id: int, session):
    profile_url = f"{BASE_URL}/?id=2&nr={cagematch_id}"
    response = requests.get(profile_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    alter_ego_section = soup.find("div", class_="InformationBoxTitle", string="Alter egos:")
    if not alter_ego_section:
        print("🔍 No alter egos found.")
        return

    alter_ego_table = alter_ego_section.find_parent("div", class_="InformationBoxRow")
    if not alter_ego_table:
        print("⚠️ Alter ego table structure unexpected.")
        return

    wrestler = session.query(Wrestler).get(wrestler_id)
    wrestler_name = wrestler.name if wrestler else ""

    gimmick_links = alter_ego_table.find_all("a", href=True)
    for link in gimmick_links:
        gimmick_name = link.text.strip()
        gimmick_url = BASE_URL + "/" + link["href"].lstrip("/")


        # Append &page=4 to force match history view
        if "&page=4" not in gimmick_url:
            gimmick_url += "&page=4"

        try:
            dates = get_gimmick_match_dates(gimmick_url)
            # Check for duplicate gimmick (by name + wrestler)
            existing = session.query(Gimmick).filter_by(
                wrestler_id=wrestler_id,
                gimmick_name=gimmick_name
            ).first()

            if existing:
                print(f"⚠️ Skipping duplicate gimmick: {gimmick_name}")
                continue

            promotion = get_or_create_promotion(session, dates["debut_promotion_name"]) if dates[
                "debut_promotion_name"] else None
            debut_promotion_id = promotion.id if promotion else None
            is_default = gimmick_name.strip().lower() == wrestler_name.strip().lower()

            gimmick = Gimmick(
                wrestler_id=wrestler_id,
                gimmick_name=gimmick_name,
                debut_promotion_id=debut_promotion_id,
                is_default=is_default,
                date_created=dates["date_created"],
                last_seen=dates["last_seen"]
            )
            session.add(gimmick)
            print(f"✅ Added gimmick: {gimmick_name}")
        except Exception as e:
            print(f"❌ Failed to process gimmick '{gimmick_name}': {e}")

    session.commit()
