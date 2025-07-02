from bs4 import BeautifulSoup
import requests
import csv
from urllib.parse import urljoin
from datetime import datetime

BASE_URL = "https://books.toscrape.com/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None
    return BeautifulSoup(response.text, 'lxml')

def scrape_books():
    books = []
    url = BASE_URL + 'catalogue/page-1.html'
    while url:
        print(f"Scraping {url}....")
        soup = get_soup(url)
        if soup is None:
            break

        for book in soup.find_all('article', class_='product_pod'):
            title = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            stock = book.find('p', class_='instock availability').text.strip()
            rating = book.p['class'][1]

            books.append({
                'Title': title,
                'Price': price,
                'Stock': stock,
                'Rating': rating
            })

        next_button = soup.find('li', class_='next')
        if next_button:
            next_page = next_button.a['href']
            url = urljoin(url, next_page)
        else:
            url = None

    return books

def save_to_csv(data, filename):
    if not data:
        print("No books found. Exiting.")
        return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Saved {len(data)} books to {filename}")

if __name__ == '__main__':
    books_data = scrape_books()
    today = datetime.now().strftime('%Y-%m-%d')
    save_to_csv(books_data, f'books_{today}.csv')
