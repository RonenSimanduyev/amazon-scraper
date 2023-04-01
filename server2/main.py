from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import requests
from google.oauth2.credentials import Credentials
import datetime
import json
import pygsheets 
from test import getToken
from typing import List
from time import time
from urllib.parse import urlencode
from scrapper import scrape_amazon_link_and_get_reviews
import numpy as np
from time import sleep


link='https://www.amazon.com/-/he/Everlast-%D7%A1%D7%98-%D7%97%D7%9C%D7%A7%D7%99%D7%9D-%D7%AA%D7%99%D7%A7-%D7%9E%D7%94%D7%99%D7%A8%D7%95%D7%AA/dp/B00005R2GR/ref=sr_1_4?crid=JH9TT2VXTZ03&keywords=speed+bag+platform&qid=1675947389&refinements=p_36%3A1253557011&rnid=386589011&s=sporting-goods&sprefix=speed+bag+platform+%2Caps%2C311&sr=1-4'
api_key = '32f7ce8c6b164aff90a2c1aa54b1c14c'
amazon_url = 'https://www.amazon.com'
openai.api_key = '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'
app = FastAPI()



origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    amazonLink : str




def askGpt(reviews: List[str],summarized_reviews:List[str]):
    response = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = f'sum this reviews{reviews}',
        temperature = 0.6,
        max_tokens = 150,
    )
    message = (response.choices[0].text)
    summarized_reviews.append(message)
    return summarized_reviews

def askGptAndInsertIntoSheets(reviews: List[str]):
    response = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = f'sum this reviews{reviews}',
        temperature = 0.6,
        max_tokens = 150,
    )
    message = (response.choices[0].text)
    client = pygsheets.authorize(service_account_file=".\pgysheets.json")
    spreadsht = client.open("connect AI")
    worksht = spreadsht.sheet1
    worksht.cell(f"A1").set_text_format("bold", True).value = message
    return  message

def remove_uselse_word(data):
    while "Prime" in data:
        data.remove("Prime")
    return data


@app.get("/")
async def create_item(item: Item):
    return "hello word"

    


@app.post('/runScript')
async def run_script():
    t=time()
    print ('we got a request from the front end')
    data = scrape_amazon_link_and_get_reviews(link)
    print(f'scraped all the data in {time() - t}')
    data = remove_uselse_word(data)
    split_size = 30
    splitted_list = [data[i:i+split_size] for i in range(0, len(data), split_size)]
    summarized_reviews=[]
    print(f'srating to send the reviews')
    for array in splitted_list:
        summarized_reviews = askGpt(array,summarized_reviews)
    print('sending the data google sheets')
    final_message=askGptAndInsertIntoSheets(summarized_reviews)
    print(f'is all tool {time() -t} seconds')
    return final_message














