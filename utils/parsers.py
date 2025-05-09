# utils/parsers.py

import re

def parse_height(height_str: str) -> float:
    """Convert '6 ft 2 in' or '6'2"' format to float like 6.2"""
    match = re.search(r"(\d+)\s*(ft|')\s*(\d+)?", height_str)
    if match:
        feet = int(match.group(1))
        inches = int(match.group(3) or 0)
        return round(feet + inches / 12.0, 2)
    return None

def parse_weight(weight_str: str) -> float:
    match = re.search(r"(\d+)", weight_str.replace(',', ''))
    return float(match.group(1)) if match else None

def parse_years_active(experience_str: str) -> int:
    match = re.search(r"(\d+)", experience_str)
    return int(match.group(1)) if match else None