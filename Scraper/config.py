import os
from dotenv import load_dotenv
from pathlib import Path

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
GENDERS = ["MALE", "FEMALE"]

ROOT_DIR = Path(__file__).parent.parent 
RAW_DATA_DIR = ROOT_DIR / 'Data' / 'raw'
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True) 

AREAS = {
    "perungalathur_vandalur": {
        "searchParam": (
            "W3sibGF0IjoxMi45MDQ4NzAzLCJsb24iOjgwLjA4NDU2MjMsInBsYWNlSWQiOiJDaElKR3plS1VJYjFVam9SMVN0"
            "TVQ0cmtLbWciLCJwbGFjZU5hbWUiOiJQZXJ1bmdhbGF0aHVyIiwic2hvd01hcCI6ZmFsc2V9LHsibGF0IjoxMi45"
            "MTczNzk5LCJsb24iOjgwLjA4NTg3NzI5OTk5OTk5LCJwbGFjZUlkIjoiQ2hJSjg2SFNVWTMxVWpvUkd6bi1Kcmkw"
            "YjZNIiwicGxhY2VOYW1lIjoiT2xkIFBlcnVuZ2FsYXRodXIiLCJzaG93TWFwIjpmYWxzZX0seyJsYXQiOjEyLjg5"
            "MTI1NTksImxvbiI6ODAuMDgxMDAwODk5OTk5OTksInBsYWNlSWQiOiJDaElKeTd0MHhnbjJVam9STV9iaG53ZzJy"
            "QjgiLCJwbGFjZU5hbWUiOiJWYW5kYWx1ciIsInNob3dNYXAiOmZhbHNlfV0="
        ),
        "locality": "Perungalathur,New Perungalathur,Old Perungalathur,Vandalur",
    },

    'tambaram': {
        'searchParam': (
            'W3sibGF0IjoxMi45MjA4MjYsImxvbiI6ODAuMTMwNjMwNCwicGxhY2VJZCI6IkNoSUpvd0pfWkJSZlVqb1JwVlFnVzc'
            '3SVNRcyIsInBsYWNlTmFtZSI6IkVhc3QgVGFtYmFyYW0iLCJzaG93TWFwIjpmYWxzZX0seyJsYXQiOjEyLjkzNzE3Nj'
            'IsImxvbiI6ODAuMTExMjMxMywicGxhY2VJZCI6IkNoSUpNNVhTbTNwZlVqb1IzV1hSbjUzTjUtZyIsInBsYWNlTmFt'
            'ZSI6IlRhbWJhcmFtIFdlc3QiLCJzaG93TWFwIjpmYWxzZX0seyJsYXQiOjEyLjkyNDUwNjEsImxvbiI6ODAuMTE1NTg'
            '0OCwicGxhY2VJZCI6IkVpNUhVMVFnVW05aFpDd2dWR0Z0WW1GeVlXMHNJRU5vWlc1dVlXa3NJRlJoYldsc0lFNWhaSF'
            'VzSUVsdVpHbGgiLCJwbGFjZU5hbWUiOiJHU1QgUm9hZC1UYW1iYXJhbSIsInNob3dNYXAiOmZhbHNlfV0='
        ),
        'locality': 'East Tambaram,Tambaram West,GST Road-Tambaram'
    },

    'sholinganallur': {
        'searchParam': (
            'W3sibGF0IjoxMi45MDA5ODc3LCJsb24iOjgwLjIyNzkzMDEsInBsYWNlSWQiOiJDaElKR3poXzNubGJVam9SR3pfLWl0U'
            'XR1XzgiLCJwbGFjZU5hbWUiOiJTaG9saW5nYW5hbGx1ciIsInNob3dNYXAiOmZhbHNlfSx7ImxhdCI6MTIuODMzNzczLC'
            'Jsb24iOjgwLjIyODY0OTgsInBsYWNlSWQiOiJFaXRQVFZJc0lFdGhjbUZ3Y0dGcllXMHNJRU5vWlc1dVlXa3NJRlJoYld'
            'sc0lFNWhaSFVzSUVsdVpHbGgiLCJwbGFjZU5hbWUiOiJPTVItS2FyYXBwYWthbSIsInNob3dNYXAiOmZhbHNlfSx7Imxh'
            'dCI6MTIuOTE5MDUxOSwibG9uIjo4MC4yMzAwMzQzLCJwbGFjZUlkIjoiQ2hJSm01WjR1NHBjVWpvUnZJbFdWcUdEQWp3I'
            'iwicGxhY2VOYW1lIjoiS2FyYXBha2thbSIsInNob3dNYXAiOmZhbHNlfV0='
        ),
        'locality': 'Sholinganallur,OMR-Karappakam,Karapakkam'
    },

    'tharamani_ecr': {
        'searchParam': (
            'W3sibGF0IjoxMi45ODYyNzksImxvbiI6ODAuMjQzMjQ4NywicGxhY2VJZCI6IkNoSUpFMTR6SDRs'
            'blVqb1J5WEZZVE03UllLMCIsInBsYWNlTmFtZSI6IlRoYXJhbWFuaSIsInNob3dNYXAiOmZhbHNl'
            'fSx7ImxhdCI6MTIuOTcyNzQyNSwibG9uIjo4MC4yNDkyOTMyOTk5OTk5OSwicGxhY2VJZCI6IkNo'
            'SUoxMUh0LTJ0ZFVqb1IzTTdRdnU4OE9kNCIsInBsYWNlTmFtZSI6Ik1hcmFpbWFsYWkgTmFnYXIi'
            'LCJzaG93TWFwIjpmYWxzZX0seyJsYXQiOjEyLjk4MTUxMzYsImxvbiI6ODAuMjU5MzMyNSwicGxh'
            'Y2VJZCI6IkVqcEZZWE4wSUVOdllYTjBJRlJ2WVdRc0lGUm9hV1ExZG1GdWJXbDVkWElzSUVOb1pX'
            'NXVZV2tzSUZSaGJXbHNJRTVoWkhVc0lFbHVaR2xoIiwicGxhY2VOYW1lIjoiRWFzdCBDb2FzdCBS'
            'b2FkLVRoaXJ1dmFubWl5dXIiLCJzaG93TWFwIjpmYWxzZX1d'
        ),
        'locality': 'Tharamani,Maraimalai Nagar,East Coast Road-Thiruvanmiyur'
    },

    'velachery_iit': {
        'searchParam': (
            'W3sibGF0IjoxMi45NzU0NjA1LCJsb24iOjgwLjIyMDcwNDcsInBsYWNlSWQiOiJDaElKTzFvRzhw'
            'OWRVam9SekRoQVlCVlFRMlkiLCJwbGFjZU5hbWUiOiJWZWxhY2hlcnkiLCJzaG93TWFwIjpmYWxz'
            'ZX0seyJsYXQiOjEyLjk4ODAyODgsImxvbiI6ODAuMjA0NzEzMzAwMDAwMDEsInBsYWNlSWQiOiJD'
            'aElKNWJfWXpQZGRVam9SMUhJRnRoZnAxTG8iLCJwbGFjZU5hbWUiOiJBZGFtYmFra2FtIiwic2hv'
            'd01hcCI6ZmFsc2V9LHsibGF0IjoxMi45OTE1NjM5LCJsb24iOjgwLjIzMzY4NTcsInBsYWNlSWQi'
            'OiJDaElKYXd6Tzg0Rm5Vam9SVUxOdFRQaU5Oa0UiLCJwbGFjZU5hbWUiOiJJbmRpYW4gSW5zdGl0'
            'dXRlIE9mIFRlY2hub2xvZ3kiLCJzaG93TWFwIjpmYWxzZX1d'
        ),
        'locality': 'Velachery,Adambakkam,Indian Institute Of Technology'
    },

    'thiruvanmiyur': {
        'searchParam': (
            'W3sibGF0IjoxMi45ODMwMjY5LCJsb24iOjgwLjI1OTQwMDEsInBsYWNlSWQiOiJDaElKYl93N20x'
            'dGRVam9ScWd2NWFYYjVXV2siLCJwbGFjZU5hbWUiOiJUaGlydXZhbm1peXVyIiwic2hvd01hcCI6'
            'ZmFsc2V9LHsibGF0IjoxMi45ODU1MTMxLCJsb24iOjgwLjI1NjUyNTYsInBsYWNlSWQiOiJDaElK'
            'VGNfRzZWNWRVam9SMG5WaVRidzFYTEEiLCJwbGFjZU5hbWUiOiJLYW1hcmFqIE5hZ2FyIiwic2hv'
            'd01hcCI6ZmFsc2V9LHsibGF0IjoxMi45NjgyMTI2LCJsb24iOjgwLjI1OTk0MjcsInBsYWNlSWQi'
            'OiJDaElKdjRFSU5UOWRVam9SazN5VG1HSDFRdjAiLCJwbGFjZU5hbWUiOiJLb3R0aXZha2thbSIs'
            'InNob3dNYXAiOmZhbHNlfV0='
        ),
        'locality': 'Thiruvanmiyur,Kamaraj Nagar,Kottivakkam'
    },

    'guindy_saidapet': {
        'searchParam': (
            'W3sibGF0IjoxMy4wMDY2NjI1LCJsb24iOjgwLjIyMDYzNjksInBsYWNlSWQiOiJDaElKZlFxa21u'
            'Qm5Vam9SVUNkUl9KV0dOTW8iLCJwbGFjZU5hbWUiOiJHdWluZHkiLCJzaG93TWFwIjpmYWxzZX0s'
            'eyJsYXQiOjEzLjAyMTI4MDUsImxvbiI6ODAuMjIzMTAzNywicGxhY2VJZCI6IkNoSUppMFFNb1Jw'
            'blVqb1JBeGc1NG8ydExQWSIsInBsYWNlTmFtZSI6IlNhaWRhcGV0Iiwic2hvd01hcCI6ZmFsc2V9'
            'LHsibGF0IjoxMi45OTc0ODczLCJsb24iOjgwLjIwMDYzNzEsInBsYWNlSWQiOiJDaElKenk4eFQw'
            'Tm5Vam9SMFZ6LTZVbUtHZmsiLCJwbGFjZU5hbWUiOiJBbGFuZHVyIiwic2hvd01hcCI6ZmFsc2V9'
            'XQ=='
        ),
        'locality': 'Guindy,Saidapet,Alandur'
    },

    'vadapalani_kodambakkam': {
        'searchParam': (
            'W3sibGF0IjoxMy4wNDk5NzExLCJsb24iOjgwLjIxMjEzMDYsInBsYWNlSWQiOiJDaElKWDhRSVdy'
            'OW1Vam9SSXhkX2ZzM2hlSlEiLCJwbGFjZU5hbWUiOiJWYWRhcGFsYW5pIiwic2hvd01hcCI6ZmFs'
            'c2V9LHsibGF0IjoxMy4wMzczMjIyLCJsb24iOjgwLjIxMjMxMTUsInBsYWNlSWQiOiJDaElKbzRp'
            'dGRONW1Vam9SMUJzOGVJZ3RoQTAiLCJwbGFjZU5hbWUiOiJBc2hvayBOYWdhciIsInNob3dNYXAi'
            'OmZhbHNlfSx7ImxhdCI6MTMuMDUyMTAxOSwibG9uIjo4MC4yMjU1Mjg1OTk5OTk5OSwicGxhY2VJ'
            'ZCI6IkNoSUprOXpYWnZCbVVqb1J4Y2trT212aDZ2byIsInBsYWNlTmFtZSI6IktvZGFtYmFra2Ft'
            'Iiwic2hvd01hcCI6ZmFsc2V9XQ=='
        ),
        'locality': 'Vadapalani,Ashok Nagar,Kodambakkam'
    },
}


# import base64
# import json

# decoded = base64.b64decode(SEARCH_PARAMS).decode()

# print(decoded)