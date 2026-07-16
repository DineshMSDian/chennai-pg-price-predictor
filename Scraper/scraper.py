import requests
from dotenv import load_dotenv
import os

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

def parse_listing(item):
    rows = []
    
    amenities = item.get("amenitiesMap") or {}   # PG-level
    rules = item.get("rulesMap") or {}
    room_types = item.get("roomTypes") or [{}]   # fallback: at least one empty room

    for rt in room_types:
        room_amenities = rt.get("amenitiesMap") or {}
        
        rows.append({
    
            "id": item.get("id"),
            "title": item.get("propertyTitle"),
            "locality": item.get("nbLocality") or item.get("locality"),
            "gender": item.get("gender"),
            "gate_closing_time": item.get("gateClosingTime"),
            
         
            "occupancy": rt.get("occupancy"),   # SINGLE / DOUBLE / TRIPLE
            "rent": rt.get("rent"),
            "deposit": rt.get("deposit"),
            
       
            "food_included": item.get("foodIncluded"),
            "breakfast": item.get("breakfast"),
            "lunch": item.get("lunch"),
            "dinner": item.get("dinner"),
            
      
            "wifi": amenities.get("WIFI"),
            "laundry": amenities.get("LAUNDRY"),
            "power_backup": amenities.get("POWER_BACKUP"),
            
    
            "nonveg_allowed": rules.get("NONVEG"),
            "smoking_allowed": rules.get("SMOKING"),
            
       
            "url": "https://www.nobroker.in" + item.get("detailUrl", ""),
        })
    
    return rows


# Test it on the first listing
test_rows = parse_listing(listings[0])
print(f"Got {len(test_rows)} rows from 1 listing")
print(test_rows[0])