# bootstrap.py

from database.db_utils import init_db, get_session
from scrapers.promotion_scraper import scrape_promotions_list, save_promotions_to_db

def bootstrap():
    print("📦 Initializing database...")
    init_db()

    print("🌍 Scraping promotions from Cagematch.net...")
    session = get_session()
    promotions = scrape_promotions_list()
    save_promotions_to_db(promotions, session)

    print(f"✅ Inserted {len(promotions)} promotions. Bootstrap complete.")

if __name__ == "__main__":
    bootstrap()