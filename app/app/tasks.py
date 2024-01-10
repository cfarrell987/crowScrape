from celery import shared_task


from .models import Item, Price
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import redis
from django.test import RequestFactory
from .utils.utils import collect_products, track_price


@shared_task
def update_prices():
    items = Item.objects.all()

    for item in items:
        # Scraping the webpage
        response = requests.get(item.item_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extracting price and currency information
        price_meta = soup.find("meta", itemprop="price")
        currency_meta = soup.find("meta", itemprop="priceCurrency")

        if price_meta:
            price = price_meta.get("content")
        else:
            continue

        if currency_meta:
            currency = currency_meta.get("content")
        else:
            continue

        # Save updated price to the database
        Price.objects.create(item=item, price=price, currency=currency)


@shared_task
def process_products():
    print("Starting Task")
    r = redis.StrictRedis(host="localhost", port=6379, db=0)  # Connect to Redis
    i = 0
    category = r.smembers("category")
    # Get new URLs from Redis
    urls_bytes = r.smembers("new_urls")  # Assuming URLs are stored in a Redis set
    new_urls = [url.decode("utf-8") for url in urls_bytes]
    for url in new_urls:
        request_factory = RequestFactory()
        payload = {"url": url, "category": category}
        print(payload)
        result = request_factory.post("/track_price/", payload)
        print(result)  # Output the result (for demonstration purposes)
        response = track_price(result)
        print(response)
        if response.status_code == 200:
            r.srem("new_urls", url)  # Remove the URL from the Redis set 'new_urls'
        else:
            i = +1

    if i < 1:
        r.delete("new_urls")  # Remove the 'new_urls' key from Redis
        r.delete("category")  # Remove the 'category' key from Redis


@shared_task
def collect_bulk():
    r = redis.StrictRedis(
        host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True
    )
    url = r.get("bulk_url")
    print("URL: ", url)
    category = r.get("bulk_category")
    if url is not None and category is not None:
        collect_products(url, category)
        r.delete("bulk_url")
        r.delete("bulk_category")
