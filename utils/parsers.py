
import re
from datetime import datetime

def parse_height(height_str: str) -> int:
    match = re.search(r"\((\d+)\s*cm\)", height_str)
    return int(match.group(1)) if match else None

def parse_weight(weight_str: str) -> int:
    match = re.search(r"\((\d+)\s*kg\)", weight_str)
    return int(match.group(1)) if match else None
def parse_years_active(experience_str: str) -> int:
    match = re.search(r"(\d+)", experience_str)
    return int(match.group(1)) if match else None

def parse_date(date_str: str) -> datetime:
    formats = ["%d.%m.%Y", "%m.%Y", "%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None
