from celery import shared_task
from .models import Item, Price
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from .views import track_price
import redis
from django.test import RequestFactory
@shared_task
def update_prices_daily():
    items = Item.objects.all()

    for item in items:
        # Scraping the webpage
        response = requests.get(item.item_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extracting price and currency information
        price_meta= soup.find('meta', itemprop='price')
        currency_meta = soup.find('meta', itemprop='priceCurrency')
        
        if price_meta:
            price = price_meta.get('content')
        else:
            continue
        
        if currency_meta:
            currency = currency_meta.get('content')
        else:
            continue

        # Save updated price to the database
        Price.objects.create(item=item, price=price, currency=currency)

@shared_task
def process_products():
    print("Starting Task")
    r = redis.StrictRedis(host='localhost', port=6379, db=0)  # Connect to Redis
    i=0
    # Get new URLs from Redis
    urls_bytes = r.smembers('new_urls')  # Assuming URLs are stored in a Redis set
    new_urls = [url.decode('utf-8') for url in urls_bytes]
    for url in new_urls:
        request_factory = RequestFactory()
        payload = {'url': url}  
        print(payload)
        result = request_factory.post('/track_price/', payload)
        print(result)  # Output the result (for demonstration purposes)
        response = track_price(result)
        print(response)
        if response.status_code == 200:
            r.srem('new_urls', url)  # Remove the URL from the Redis set 'new_urls'
        else:
           i=+1

    if i < 1:
        r.delete('new_urls')  # Remove the 'new_urls' key from Redis