import math
import asyncio
import aiohttp
import requests
from time import time
from typing import List
from urllib.parse import urlencode
import numpy as np


api_key = '32f7ce8c6b164aff90a2c1aa54b1c14c'
amazon_url = 'https://www.amazon.com'


def get_html(url: str):
    params = {'api_key': api_key, 'url': url}
    t = time()
    r = requests.get('http://api.scraperapi.com/', params=urlencode(params))
    t = time() - t
    r.raise_for_status()
    print(f'fetched html in {t} seconds, from url: {url}\n')
    return r.text


def get_reviews_url(review_url_route: str, page_number: int):
    return f'{amazon_url}{review_url_route}&pageNumber={page_number}'


def get_review_url_route(html: str):
    p1 = html.split('data-hook="see-all-reviews-link-foot"', 1)
    p2 = p1[1].split('href="', 1)
    p3 = p2[1].split('"', 1)
    review_url_route = p3[0]
    return review_url_route


def get_total_review_count(html: str):
    p1 = html.split('data-hook="total-review-count"', 1)
    p2 = p1[1].split('</span>', 1)
    p3 = p2[0].rsplit('>', 1)
    p4 = p3[1].strip().split(' ', 1)
    total_review_count = p4[0]
    print(f'parsed total review count: {total_review_count}')
    return total_review_count


def add_review_page_reviews(html: str, reviews: List[str]):
    try:
        reviews_split = html.split('data-hook="review-body"')
        for i in reviews_split:
            review = i.split('<span>', 1)[1].split('</span>', 1)[0].strip()
            reviews.append(review)
    except Exception as e:
        print("add_review_page_reviews failed:", e)
        print(html)
        raise e


def get_review_count(html: str, total_review_count: str):
    p1 = html.split('data-hook="cr-filter-info-review-rating-count"', 1)
    p2 = p1[1].split('>', 1)
    p3 = p2[1].split('<', 1)
    p4 = ' '.join(p3[0].strip().split(total_review_count, 1))
    p5 = ''.join(p4.split(',')).strip()
    txt = p5.split(' ')
    review_count = [int(s) for s in txt if s.isdigit()][0]
    print(f'parsed review count: {review_count}')
    return review_count


async def scrape_page(
    session: aiohttp.ClientSession,
    review_url_route: str,
    page_number: int,
    delay: int
):
    await asyncio.sleep(delay)

    print(f'fetching reviews from page {page_number}')
    url = get_reviews_url(review_url_route, page_number)
    params = {'api_key': api_key, 'url': url}

    t = time()
    async with session.get(url='http://api.scraperapi.com/', params=params) as response:
        html = await response.text()
        t = time() - t
        print(f'fetched html in {t} seconds, from url: {url}\n')
        return html


async def scrape_all_pages(page_number: int, pages: int, review_url_route: str, reviews: List[str]):
    delay = 0
    tasks = []
    async with aiohttp.ClientSession() as session:
        while page_number < pages:
            tasks.append(scrape_page(session, review_url_route, page_number, delay))
            page_number += 1
            delay += 2
        htmls = await asyncio.gather(*tasks)
    for i in htmls:
        add_review_page_reviews(i, reviews)




def scrape_amazon_link_and_get_reviews(product_url: str) -> List[str]:
    t = time()
    print("start scraping")

    product_html = get_html(product_url)

    # print(f'fetching reviews from product link')
    # reviews = get_product_reviews(product_html)
    reviews = []
    total_review_count = get_total_review_count(product_html)
    review_url_route = get_review_url_route(product_html)
    page_number = 1
    print(f'parsed review url route {review_url_route}')
    print(f'fetching reviews from page {page_number}')

    page_url = get_reviews_url(review_url_route, page_number)
    page_html = get_html(page_url)
    add_review_page_reviews(page_html, reviews)
    page_number += 1

    review_count = get_review_count(page_html, total_review_count)
    pages = math.ceil(review_count / 10)

    # Run in sync
    while page_number < 6:
        print(f'fetching reviews from page {page_number}')
        page_url = get_reviews_url(review_url_route, page_number)
        page_html = get_html(page_url)
        add_review_page_reviews(page_html, reviews)
        page_number += 1
    




    # print(f'scraped all {len(reviews)} product reviews in {time() - t} seconds:')
    # count_duplicates = {}
    # for i in reviews:
    #     if i not in count_duplicates:
    #         count_duplicates[i] = 0
    #     count_duplicates[i] += 1

    # for i in count_duplicates:
    #     print(count_duplicates[i], i)

    return reviews


if __name__ == "__main__":
    link = 'https://www.amazon.com/Magna-Qubix-85Piece-Set-Award-Winning-Educational/dp/B07W2RB6TG/ref=sxin_15_pa_sp_search_thematic_sspa?c=ts&content-id=amzn1.sym.fe3abdfa-d248-4e07-8b0d-b8a0a47d4a6c%3Aamzn1.sym.fe3abdfa-d248-4e07-8b0d-b8a0a47d4a6c&cv_ct_cx=Building%2BToys&keywords=Building%2BToys&pd_rd_i=B07W2RB6TG&pd_rd_r=8cd60f09-ed5f-4bea-bed2-028953497261&pd_rd_w=oOlAH&pd_rd_wg=M3gl3&pf_rd_p=fe3abdfa-d248-4e07-8b0d-b8a0a47d4a6c&pf_rd_r=V2JNNNBYEE0NE0TAH47K&qid=1675270044&s=toys-and-games&sr=1-2-a73d1c8c-2fd2-4f19-aa41-2df022bcb241-spons&ts_id=166092011&ufe=app_do%3Aamzn1.fos.006c50ae-5d4c-4777-9bc0-4513d670b6bc&th=1'
    scrape_amazon_link_and_get_reviews(link)
