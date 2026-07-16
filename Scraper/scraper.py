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


resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
print(resp.status_code)
print(resp.json())