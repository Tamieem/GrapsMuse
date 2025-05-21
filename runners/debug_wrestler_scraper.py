from scrapers.wrestler_scraper import scrape_wrestler_profile
from database.db_utils import get_session

def main():
    session = get_session()
    url = "https://www.cagematch.net/?id=2&nr=761&gimmick=Undertaker"  # change this as needed
    wrestler_model = scrape_wrestler_profile(url, session)

    print("📊 Scraped Data:")
    print(wrestler_model)

if __name__ == "__main__":
    main()