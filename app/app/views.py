from django.shortcuts import render
from django.http import HttpResponse
from matplotlib import dates
from .models import Item, Price
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
import matplotlib.pyplot as plt
import io
import base64
import redis
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from .forms import ItemPriceGraphForm
# Create your views here.

def home(request):
    if request.method == 'POST':
        url = request.POST.get('url')  # Retrieve the URL from the form
        category = request.POST.get('category')
        urls_to_process = extract_urls(url, category)  # Pass the URL to the Celery task
    return render(request, 'app/home.html')

def extract_urls(url, category):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract URLs from the page using BeautifulSoup or any other method
        urls = [link.get('href') for link in soup.find_all('a', class_='product-item-link')]  # Example: Extracting href attributes from <a> tags
        #print(urls)
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.sadd('category', category)
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


    form = ItemPriceGraphForm(request.GET)
    
    # Get Item
    selected_item_id = int(request.GET.get('item_id')) if request.GET.get('item_id') else None
    
    if selected_item_id:
        selected_item = Item.objects.get(pk=selected_item_id)

        #Get Time Range
        time_ranges = {
            '7 * 24': 7 * 24,  # 7 days
            '5 * 24': 5 * 24,  # 5 days
            '24': 24,          # 24 hours
            '12': 12,          # 12 hours
        }
        
        selected_time_range = request.GET.get('time_range') if request.GET.get('time_range') else 24
        hours = time_ranges.get(selected_time_range, 24)  # Default to 24 hours if not specified
        
        # Calculate the timestamp for the selected time range
        timestamp_threshold = datetime.now() - timedelta(hours=hours)

        prices = Price.objects.filter(item_id=selected_item_id, timestamp__gte=timestamp_threshold)
        price_list = [price.price for price in prices]
        timestamp_list = [price.timestamp for price in prices]

        # Create the plot in memory
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(timestamp_list, price_list, marker='o', linestyle='-')

        # Formatting x-axis timestamps
        ax.xaxis.set_major_formatter(dates.DateFormatter('%d-%b %H:%M'))  # Day-Month hh:mm format
        plt.gcf().autofmt_xdate()

        ax.set_title(f'Price History: {selected_item.item_name} ')
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Price')
        ax.grid(True)

        # Convert plot to a base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        context = {
                    'form': form,
                    'items': items, 
                    'plot_data': plot_data}
        return render(request, 'app/item_price_graph.html', context )
    return render(request, 'app/item_price_graph.html', {'form': form, 'items': items})

def list_items(request):
    items = Item.objects.all()
    price = Price.objects.select_related()
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'app/list_items.html', {'page_obj': page_obj})