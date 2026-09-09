from dotenv import load_dotenv, find_dotenv
import os

from pydantic import BaseModel
from fastapi import FastAPI

load_dotenv(find_dotenv())

app = FastAPI()

# my kind of healt check :)
@app.get('/secret')
def easter_eggs():
    return f'I have a secret message for you, -> {os.getenv('SECRET_MSG')}'