
from scrapers.gimmick_scraper import get_gimmick_match_dates
from database.db_utils import get_session
from database.models import Wrestler
import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.cagematch.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


def extract_cagematch_id_from_url(url: str) -> int:
    match = re.search(r"id=2&nr=(\d+)", url)
    return int(match.group(1)) if match else None


def debug_scrape_gimmicks(wrestler_id: int, cagematch_id: int):
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

    gimmick_links = alter_ego_table.find_all("a", href=True)
    for link in gimmick_links:
        gimmick_name = link.text.strip()
        gimmick_url = BASE_URL + "/" + link["href"].lstrip("/")
        gimmick_cagematch_id = extract_cagematch_id_from_url(gimmick_url)

        if "&page=4" not in gimmick_url:
            gimmick_url += "&page=4"

        try:
            dates = get_gimmick_match_dates(gimmick_url)

            print(f"\n🧪 Gimmick Preview:")
            print(f"  Wrestler ID      : {wrestler_id}")
            print(f"  Gimmick Name     : {gimmick_name}")
            print(f"  Gimmick ID       : {gimmick_cagematch_id}")
            print(f"  Match History URL: {gimmick_url}")
            print(f"  Date Created     : {dates['date_created']}")
            print(f"  Last Seen        : {dates['last_seen']}")
            print(f"  Debut Promotion  : {dates['debut_promotion_name']}")
            print(f"  Is Default       : False")

        except Exception as e:
            print(f"❌ Failed to process gimmick '{gimmick_name}': {e}")


def main():
    session = get_session()
    test_cagematch_id = 932  # Batista
    wrestler = session.query(Wrestler).filter_by(cagematch_id=test_cagematch_id).first()

    if not wrestler:
        print(f"❌ Wrestler with Cagematch ID {test_cagematch_id} not found.")
        return

    print(f"\n🎯 DEBUGGING GIMMICKS FOR: {wrestler.name} (ID: {wrestler.id})\n")
    debug_scrape_gimmicks(wrestler.id, wrestler.cagematch_id)

if __name__ == "__main__":
    main()
