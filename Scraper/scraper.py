import requests
from dotenv import load_dotenv
import os
import time, random
import csv

load_dotenv()

BASE_URL = 'https://www.nobroker.in/api/v3/multi/property/PG/filter'
USER_ID = os.getenv('USER_ID')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.nobroker.in',
    'X-Origin': 'nb-search',
    'userid': USER_ID,
}

params  = {
    'city': 'chennai',
    'isMetro': 'false',
    'locality': 'East Tambaram,Tambaram West, GST Road-Tambaram',
    'pageNo': 1,
    'radius': 2.0,
    'searchParam': (
        'W3sibGF0IjoxMi45MjA4MjYsImxvbiI6ODAuMTMwNjMwNCwicGxhY2VJZCI6IkNoSUpvd0'
        'pfWkJSZlVqb1JwVlFnVzc3SVNRcyIsInBsYWNlTmFtZSI6IkVhc3QgVGFtYmFyYW0iLCJz'
        'aG93TWFwIjpmYWxzZX0seyJsYXQiOjEyLjkzNzE3NjIsImxvbiI6ODAuMTExMjMxMywicG'
        'xhY2VJZCI6IkNoSUpNNVhTbTNwZlVqb1IzV1hSbjUzTjUtZyIsInBsYWNlTmFtZSI6IlRh'
        'bWJhcmFtIFdlc3QiLCJzaG93TWFwIjpmYWxzZX0seyJsYXQiOjEyLjkyNDUwNjEsImxvbi'
        'I6ODAuMTE1NTg0OCwicGxhY2VJZCI6IkVpNUhVMVFnVW05aFpDd2dWR0Z0WW1GeVlXMHNJ'
        'RU5vWlc1dVlXa3NJRlJoYldsc0lFNWhaSFVzSUVsdVpHbGgiLCJwbGFjZU5hbWUiOiJHU1'
        'QgUm9hZC1UYW1iYXJhbSIsInNob3dNYXAiOmZhbHNlfV0='
    )
}

AREAS = {
    "perungalathur": {
        "searchParam": "YOUR_BASE64_BLOB_HERE",
        "locality": "Perungalathur,New Perungalathur,Vandalur",
    },
}

GENDERS = ["MALE", "FEMALE"]

def parse_listing(item):
    rows = []
    
    amenities = item.get("amenitiesMap") or {}   # PG-level
    rules = item.get("rulesMap") or {}
    room_types = item.get("roomTypes") or [{}]   # fallback: at least one empty room

    for rt in room_types:
        room_amenities = rt.get("amenitiesMap") or {}
        
        rows.append({
            # identity
            'id': item.get('id'),
            'title': item.get('propertyTitle'),
            'locality': item.get('nbLocality') or item.get('locality'),
            'address': item.get('address'),
            'gender': item.get('gender'),
            'available_for': item.get('availableForDesc'),

            # room
            'occupancy': rt.get('occupancy'), 
            'rent': rt.get('rent'),
            'deposit': rt.get('deposit'),
            'attached_bathroom': rt.get('attachedBathroom'),

            # food
            'food_included': item.get('foodIncluded'),
            'breakfast': item.get('breakfast'),
            'lunch': item.get('lunch'),
            'dinner': item.get('dinner'),
            'mess': amenities.get('MESS'),

            # PG-level amenities
            'wifi': amenities.get('WIFI'),
            'laundry': amenities.get('LAUNDRY'),
            'power_backup': amenities.get('POWER_BACKUP'),
            'refrigerator': amenities.get('REFRIGERATOR'),
            'common_tv': amenities.get('COMMON_TV'),
            'room_cleaning': amenities.get('ROOM_CLEANING'),
            'warden': amenities.get('WARDEN'),
            'cooking_allowed': amenities.get('COOKING'),
            'parking': item.get('parkingDesc'),

            # room-level amenities
            'room_ac': room_amenities.get('AC'),
            'room_cupboard': room_amenities.get('CUPBOARD'),
            'room_tv': room_amenities.get('TV'),
            'room_geyser': room_amenities.get('GEASER'),
            'room_bedding': room_amenities.get('BEDDING'),
            'room_attached_bath': room_amenities.get('AB'),

            # rules
            'gate_closing_time': item.get('gateClosingTime'),
            'smoking_allowed': rules.get('SMOKING'),
            'guardian_required': rules.get('GUARDIAN'),
            'nonveg_allowed': rules.get('NONVEG'),
        })
    
    return rows

def scrape_area(search_param, locality, gender):
    """Fetch all pages for one area + gender combo. Returns flat list of rows."""

    all_rows = []
    page_no = 1
    total_fetched = 0

    while True:
        print(f"  Page {page_no} | {locality} | {gender}")
        
        params = {
            "city": "chennai",
            "gender": gender,
            "isMetro": "false",
            "locality": locality,
            "pageNo": page_no,
            "radius": 2.0,
            "searchParam": search_param,
        }
        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f' HTTP error: {e}, so skipping this page')
            break
        except requests.exceptions.RequestException as e:
            print(f' Request failed: {e}, so skipping this page')
            break

        data = response.json()
        listings = data.get("data", [])

        if not listings:
            print("  No more listings. Done.")
            break
        
        for item in listings:
            all_rows.extend(parse_listing(item))

        total_fetched += len(listings)
        total_listings = data.get("otherParams", {}).get("total_count", 0)
        print(f"  Got {len(listings)} | Total available: {total_listings}")
        
        if len(all_rows) >= total_listings:
            break

        page_no += 1
        time.sleep(random.uniform(2, 4)) 

    return all_rows


all_rows = []

for area_name, cfg in AREAS.items():
    for gender in GENDERS:
        print(f"\nScraping {area_name} | {gender}")
        rows = scrape_area(cfg["searchParam"], cfg["locality"], gender)
        all_rows.extend(rows)
        time.sleep(random.uniform(2, 4))

print(f"\nTotal rows collected: {len(all_rows)}")

# Save CSV
if all_rows:
    with open("chennai_pg_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)
    print("Saved to chennai_pg_data.csv")