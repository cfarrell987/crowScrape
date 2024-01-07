from django.shortcuts import render
from django.http import HttpResponse
from .models import Item, Price
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
import matplotlib.pyplot as plt
import io
import base64
import redis
# Create your views here.

def home(request):
    if request.method == 'POST':
        url = request.POST.get('url')  # Retrieve the URL from the form
        urls_to_process = extract_urls(url)  # Pass the URL to the Celery task
    return render(request, 'app/home.html')

def extract_urls(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract URLs from the page using BeautifulSoup or any other method
        urls = [link.get('href') for link in soup.find_all('a', class_='product-item-link')]  # Example: Extracting href attributes from <a> tags
        #print(urls)
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        for u in urls:
            r.sadd('new_urls', u)
        print(r.smembers('new_urls'))
        return urls
    else:
        return []

def track_price(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        item_name = request.POST.get('item_name')  # Optional: if you want to get item name from the form
        category = request.POST.get('category')
        # Scraping the webpage
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        if not item_name:
            name_element = soup.find('span', class_='base', itemprop='name')
            if name_element:
                item_name = name_element.text.strip()
            else:
                return render(request, 'error.html', {'message': 'Failed to extract item name from the webpage.'})

        # Extracting price and currency information
        price_meta= soup.find('meta', itemprop='price')
        currency_meta = soup.find('meta', itemprop='priceCurrency')

        if price_meta:
            price = price_meta.get('content')  # Extracting price text
        else:
            price = None
        
        if currency_meta:
            currency = currency_meta.get('content')  # Extracting currency content from the meta tag
        else:
            currency = None

        # For debugging purposes, print the extracted price and currency
        print(f"Extracted Price: {price}")
        print(f"Extracted Currency: {currency}")

        if category is not None:
            pass
        else:
            category="default"

        if price is not None and currency is not None:
            # Save to database
            item, created = Item.objects.get_or_create(item_name=item_name, item_url=url, category=category)
            Price.objects.create(item=item, price=price, currency=currency)
            return render(request, 'app/success.html', {'message': 'Price tracked successfully!'})
        else:
            return render(request, 'error.html', {'message': 'Failed to extract price or currency from the webpage.'})

    return render(request, 'app/track_price.html')

def item_price_graph(request):
    # Replace this with your logic to fetch available items
    items = Item.objects.all()

    selected_item_id = request.GET.get('item_id')
    prices = Price.objects.filter(item_id=selected_item_id)
    price_list = [price.price for price in prices]
    timestamp_list = [price.timestamp for price in prices]

    # Create the plot in memory
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(timestamp_list, price_list, marker='o', linestyle='-')
    ax.set_title('Price History')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Price')
    ax.grid(True)

    # Convert plot to a base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    context = {'items': items, 'plot_data': plot_data}
    return render(request, 'app/item_price_graph.html', context)


