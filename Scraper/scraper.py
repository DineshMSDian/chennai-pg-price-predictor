import requests
import time, random
import csv
import json
from config import BASE_URL, HEADERS, AREAS, GENDERS, RAW_DATA_DIR

def parse_listing(item):
    """
    INPUT: One JSON Property (PG) from the API
    OUTPUT: A list of flat dictionaries (one per room type)

    EXAMPLE: if a PG has SINGLE, DOUBLE, TRIPPLE rroms -> 3 rows returned
    """
    rows = []
    
    amenities = item.get("amenitiesMap") or {}   # PG-level
    rules = item.get("rulesMap") or {}
    score = item.get('score') or {}
    room_types = item.get("roomTypes") or [{}]   # fallback: at least one empty room

    for rt in room_types:
        room_amenities = rt.get("amenitiesMap") or {}
        
        rows.append({
            # identity
            'id': item.get('id'),
            'title': item.get('propertyTitle'),
            'latitude': item.get('latitude'),
            'longitude': item.get('longitude'),
            'locality': item.get('nbLocality') or item.get('locality'),
            'address': item.get('address'),
            'gender': item.get('gender'),
            'available_for': item.get('availableForDesc'), 

            # score
            'transit_score': score.get('transit'),
            'lifestyle_score': score.get('lifestyle'),
            
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
            'total_bathrooms': item.get('bathroom'),

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

def scrape_all():
    all_rows = []

    for area_name, cfg in AREAS.items():
        for gender in GENDERS:
            print(f'\nScraping: {area_name} | {gender}')
            rows = scrape_area(cfg['searchParam'], cfg['locality'], gender)
            all_rows.extend(rows)
            time.sleep(random.uniform(2, 4))  

    print(f'\nTotal rows collected: {len(all_rows)}')
    return all_rows

def save_csv(rows, filename='chennai_pg_dataset.csv'):
    if not rows:
        print('No rows to save.')
        return
    path = RAW_DATA_DIR / filename
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f'Saved {len(rows)} rows to {path}')


def save_json(rows, filename='chennai_pg_dataset.json'):
    path = RAW_DATA_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f'Saved {len(rows)} rows to {path}')

if __name__ == '__main__':
    rows = scrape_all()
    save_csv(rows)
    save_json(rows)