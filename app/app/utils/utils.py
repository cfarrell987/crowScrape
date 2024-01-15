from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import redis
from app.models import Item, Price


def collect_products(url, category):
    r = redis.StrictRedis(host="localhost", port=6379, db=0)
    page = 1
    max_urls = float("-inf")
    urls_added = 0
    while True:
        paginated_url = f"{url}?p={page}&product_list_limit=36"
        response = requests.get(paginated_url, timeout=10)
        print(f"Fetching page {page} from {paginated_url}")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # print(soup)
            urls = [
                link.get("href")
                for link in soup.find_all("a", class_="product-item-link")
            ]

            if not urls:
                paginated_url = f"{url}&p={page}&product_list_limit=36"
                response = requests.get(paginated_url, timeout=10)
                print(response.status_code)
                soup = BeautifulSoup(response.content, "html.parser")
                urls = [
                    link.get("href")
                    for link in soup.find_all("a", class_="product-item-link")
                ]

            toolbar_numbers = soup.find_all("span", class_="toolbar-number")

            for toolbar_number in toolbar_numbers:
                number = int(toolbar_number.get_text(strip=True))
                if number > max_urls:
                    max_urls = number

            current_count = r.scard("new_urls")

            if not urls:
                break

            r.sadd("category", category)
            # TODO: this counter is still broken, figure out why the logic
            # isn't stopping the loop before exceeding the max urls
            if urls_added <= (max_urls + 1):
                for u in urls:
                    print(
                        f"Adding Number{urls_added} of {max_urls} to URL to Redis: {u} "
                    )
                    r.sadd("new_urls", u)
                    urls_added += 1
                    print(
                        f"Urls added: {urls_added}, Max urls: {max_urls}, Current count: {current_count}"
                    )
            else:
                print("Max urls reached")
                break
            print(f"Added URLs from page {page}", f"URL: {u}")

            page += 1
        elif response.status_code == 302:
            print("Reached the last available page. Exiting pagination.")
            break
        else:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            break


def track_price(request):
    if request.method == "POST":
        url = request.POST.get("url")
        item_name = request.POST.get("item_name")
        category = request.POST.get("category")
        # Scraping the webpage
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        if not item_name:
            name_element = soup.find("span", class_="base", itemprop="name")
            if name_element:
                item_name = name_element.text.strip()
            else:
                return render(
                    request,
                    "error.html",
                    {"message": "Failed to extract item name from the webpage."},
                )

        # Extracting price and currency information
        price_meta = soup.find("meta", itemprop="price")
        currency_meta = soup.find("meta", itemprop="priceCurrency")

        if price_meta:
            price = price_meta.get("content")  # Extracting price text
        else:
            price = None

        if currency_meta:
            currency = currency_meta.get(
                "content"
            )  # Extracting currency content from the meta tag
        else:
            currency = None

        # For debugging purposes, print the extracted price and currency
        print(f"Extracted Price: {price}")
        print(f"Extracted Currency: {currency}")

        if category is not None:
            pass
        else:
            category = "default"

        if price is not None and currency is not None:
            # Save to database
            item, created = Item.objects.get_or_create(
                item_name=item_name, item_url=url, category=category
            )
            Price.objects.create(item=item, price=price, currency=currency)
            return render(
                request, "app/success.html", {"message": "Price tracked successfully!"}
            )
        else:
            return render(
                request,
                "error.html",
                {"message": "Failed to extract price or currency from the webpage."},
            )

    return render(request, "app/track_price.html")
