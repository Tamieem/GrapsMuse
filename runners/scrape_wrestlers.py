from scrapers.wrestler_scraper import scrape_top_100_wrestlers
from database.db_utils import get_session, init_db

def main():
    print("📦 Initializing database (if needed)...")
    init_db()

    print("🤼 Scraping top 100 wrestlers from Cagematch.net...")
    session = get_session()
    scrape_top_100_wrestlers(session)

    print("✅ Done.")

if __name__ == "__main__":
    main()