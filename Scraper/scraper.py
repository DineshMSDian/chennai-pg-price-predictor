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

# PHASE 1: Fetch ONE page from the API (no loop here)
def fetch_page(search_param, locality, gender, page_no):
    """
    Do one single HTTP request to nobroker for a specific page
    
    INPUT:
        search_param: encoded string for the area
        locality: comma seperated locality names
        gender: 'MALE' or 'FEMALE'
        page_no: which page number (1,2,3...)

    OUTPUT:
        - listings: list of property JSON objects on this page
        - total_count: total number of listings available (from API)
    """

    params = {
        "city": "chennai",
        "gender": gender,
        "isMetro": "false",
        "locality": locality,
        "pageNo": page_no,
        "radius": 2.0,
        "searchParam": search_param,
    }

    print(f'Fetching page {page_no} for {gender} in {locality.split(',')[0]}')

    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status() # raise an error if status is 4xx/5xx
    except requests.exceptions.RequestException as e:
        print(f'Error : {e}')
        return [], 0 # return empty list andd 0 tota;

    data = response.json()
    listings = data.get('data', [])
    total_count = data.get('otherParams', {}).get('total_count', 0)

    print(f'Got {len(listings)} Listings. Total available: {total_count}')
    return listings, total_count

# PHASE 2: Scrape ALL pages for ONE area + gender
def scrape_area(search_param, locality, gender):
    """
    Fetches All pages for a single (area, gender) combination.
    uses Pagination: starts at page 1, keeps going untill we have everything

    Why pagination?
    the API returns only ~20 listings per page, if there are 70 total,
    we need to fetch pages 1, 2, 3 and so on to get all 70

    How we know when to stop?
    we compare len(all_rows) vs total count, when all rows >= total_counts, we're done scraping

    Returns:
        all_rows: list of all rows
    """

    all_rows = [] # this will holds the all flattened rows for this area + gender
    page_no = 1 # starts at page 1
    total_fetched = 0

    while True:
        # 1. fetch one page
        listings, total_count = fetch_page(search_param, locality, gender, page_no)

        # 2. if no listings come back, we're done scraping
        if not listings:
            print('No listings on this page, Scraping Stopped')

        # 3. convert each JSON property into flat rows and add to the list
        for each_property in listings:
            flat_rows = parse_listing(each_property) # returns a list (1 per room)
            all_rows.extend(flat_rows) # add them to the master list

        # 4. Check if we have scraped everything
        if total_count and len(all_rows) >= total_count:
            print(f'Scraped all {total_count} listings')
            break

        # 5. if not done, move to next page
        page_no += 1

        # 6. to avoid rate limiting
        time.sleep(random.uniform(2, 4)) 

    return all_rows

# PHASE 3: Scrape EVERYTHING (All areas × All genders)
def scrape_all():
    """
    Loops through:
        - Every area in AREAS dict
        - Every gender in GENDERS dict

    for each combinagtion, it calls scrape_area() to get all pages
    then it combine all results into one master list
    """
    all_rows = [] # the final master list, containg evrything

    for area_name, area_config in AREAS.items():
        search_param = area_config['searchParam']
        locality = area_config['locality']

        for gender in GENDERS:
            print(f'\nScraping: {area_name} | {gender}')

            # Fetch all pages for this (area + gender) combination
            rows = scrape_area(search_param, locality, gender)

            # add these rows to the master list
            all_rows.extend(rows)

            print(f'COllected {len(rows)} rows for {area_name} / {gender}')
            print(f'Total Rows so far {len(all_rows)}')

            # to avoid rate limit, short pause between area/gender switches
            time.sleep(random.uniform(1, 2))

    print(f'\nScraping COMPLETED! total rows collected: {len(all_rows)}')
    return all_rows

# PHASE 4: Save the data to files
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
    if not rows:
        print('No rows to save')
        return
    
    path = RAW_DATA_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f'Saved {len(rows)} rows to {path}')

# PHASE 5: The Main Entry Point (Runs when you execute the script)
if __name__ == '__main__':
    """
    this is the Starting line of the script

    the flow is:
        1. scrape_all() -> fetches all pages
        2. save_csv() -> saves to CSV file
        3. save_json() -> save to JSON file
    """

    scrape_data = scrape_all()
    save_csv(scrape_data)
    save_json(scrape_data)