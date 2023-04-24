import os

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import urllib.parse
from webscraper.database import connector, dataHandler
page_size = 96
page_num = 1
start_url = 'https://www.newegg.ca/Internal-SSDs/SubCategory/ID-636/Page-' + str(
    page_num) + '?Tid=11700&PageSize=' + str(
    page_size)


def get_pages(page_num, start_url):
    total_pages = 0

    if page_num == 1:
        response = requests.get(start_url)
        if response.status_code == 200:
            soup = bs(response.content, 'html.parser')
            results = soup.find_all('div', class_='list-tools-bar')
            pages = results[0].find('span', class_='list-tool-pagination-text').get_text()
            pages = pages.replace('Page', '')
            current_page = pages.split('/')[0]
            total_pages = pages.split('/')[1]
            page_num = int(current_page)
            total_pages = int(total_pages)
    return page_num, total_pages


def get_all_item_details_per_page(start_url):
    url = start_url
    response = requests.get(url)
    item_name = []
    item_price = []
    item_url = []

    if response.status_code == 200:
        soup = bs(response.content, 'html.parser')
        results = soup.find_all('div', class_='item-cell')

        for soup in results:
            try:
                item_name.append(soup.find('a', class_='item-title').get_text())
            except:
                item_name.append('None')
            try:
                item_price.append(soup.find('li', class_='price-current').get_text())
            except:
                item_price.append('None')
            try:
                item_url.append(soup.find('a', class_='item-title').get('href'))
            except:
                item_url.append('None')

    else:
        print('Error: ' + str(response.status_code))

    return item_name, item_price, item_url


def get_all_pages(page_size, page_num, total_pages, start_url):
    item_name = []
    item_price = []
    item_url = []

    for page_num in range(page_num, total_pages):
        page_num += 1
        start_url = 'https://www.newegg.ca/Internal-SSDs/SubCategory/ID-636/Page-' + str(
            page_num) + '?Tid=11700&PageSize=' + str(page_size)
        print('Page: ' + str(page_num))
        name, price, url = get_all_item_details_per_page(start_url)
        item_name.extend(name)
        item_price.extend(price)
        item_url.extend(url)

    return item_name, item_price, item_url


def format_items(item_name, item_price, item_url):
    item_name = pd.DataFrame(item_name, columns=['item_name'])
    item_price = pd.DataFrame(item_price, columns=['item_price'])
    item_url = pd.DataFrame(item_url, columns=['item_url'])
    item_price['item_price'] = item_price['item_price'].str.extract('(\d+\.\d+)', expand=False)
    items = pd.concat([item_name, item_price, item_url], axis=1)
    return items


page_num, total_pages = get_pages(page_num, start_url)
get_items = get_all_pages(page_size, page_num, total_pages, start_url)
items = format_items(get_items[0], get_items[1], get_items[2])


# items.to_csv('items.csv', index=False)

# database_config = os.path.join(os.path.dirname(__file__), 'config\\database.cfg')
database_config = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config\\database.cfg'))

engine = connector.init_engine(database_config, 'postgresql')
conn = connector.create_connection(engine)
connector.close_connection(conn)
dataHandler.insert_item_data(engine, items)
