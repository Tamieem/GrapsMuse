import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from datetime import datetime

def parse_height_to_inches(height_str):
    match = re.search(r'(\d+)\s*ft\s*(\d*)\s*in*', height_str.lower())
    if match:
        feet = int(match.group(1))
        inches = int(match.group(2)) if match.group(2) else 0
        return feet * 12 + inches
    return None

def parse_weight_to_lbs(weight_str):
    match = re.search(r'(\d+)\s*lbs', weight_str.lower())
    return int(match.group(1)) if match else None

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%b %d, %Y').date()
    except:
        return None

# Connect DB and ensure schema
conn = sqlite3.connect("cagematch.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Wrestlers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    real_name TEXT,
    promotion INTEGER,
    height_inches INTEGER,
    weight_lb INTEGER,
    height_str TEXT,
    weight_str TEXT,
    debut DATE,
    is_active BOOLEAN,
    years_active INTEGER,
    retirement DATE
)
""")
conn.commit()

def scrape_wrestler(wrestler_id):
    url = f'https://www.cagematch.net/?id=2&nr={wrestler_id}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    name = soup.find('h1').text.strip()
    profile_table = soup.find('table', class_='InformationBox')
    profile_data = {row.find_all('td')[0].text.strip(): row.find_all('td')[1].text.strip()
                    for row in profile_table.find_all('tr') if len(row.find_all('td')) == 2}

    real_name = profile_data.get("Birth Name", "")
    height_str = profile_data.get("Height", "")
    weight_str = profile_data.get("Weight", "")
    debut_str = profile_data.get("Debut", "")
    debut = parse_date(debut_str)

    height_inches = parse_height_to_inches(height_str)
    weight_lb = parse_weight_to_lbs(weight_str)

    years_active = None
    is_active = True
    retirement = None

    if "In Ring Experience" in profile_data:
        match = re.search(r'(\d+)', profile_data["In Ring Experience"])
        years_active = int(match.group(1)) if match else None

    if "End of In-Ring Career" in profile_data:
        retirement_str = profile_data["End of In-Ring Career"]
        retirement = parse_date(retirement_str)
        is_active = False

    promotion_id = None  # Future enhancement

    cursor.execute("""
        INSERT OR REPLACE INTO Wrestlers (
            id, name, real_name, promotion,
            height_inches, weight_lb, height_str, weight_str,
            debut, is_active, years_active, retirement
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (wrestler_id, name, real_name, promotion_id,
          height_inches, weight_lb, height_str, weight_str,
          debut, is_active, years_active, retirement))

    conn.commit()
    print(f"Saved: {name} (ID: {wrestler_id})")

# Example: Undertaker (has retirement date)
scrape_wrestler(761)
conn.close()