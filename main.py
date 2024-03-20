from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import json

BASE_URL = 'http://quotes.toscrape.com'

def get_quotes(page=1):
    quotes = []
    authors = {}
    while True:
        response = requests.get(f"{BASE_URL}/page/{page}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        quote_divs = soup.find_all('div', class_='quote')
        
        if not quote_divs:
            break
        
        for quote_div in quote_divs:
            text = quote_div.find('span', class_='text').get_text(strip=True)
            author = quote_div.find('small', class_='author').get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote_div.find_all('a', class_='tag')]
            
            quote_data = {'quote': text, 'author': author, 'tags': tags}
            quotes.append(quote_data)
            
            if author not in authors:
                author_url = quote_div.find('a')['href']
                author_response = requests.get(f"{BASE_URL}{author_url}")
                author_soup = BeautifulSoup(author_response.text, 'html.parser')
                
                full_name = author_soup.find('h3', class_='author-title').get_text(strip=True)
                born_date = author_soup.find('span', class_='author-born-date').get_text(strip=True)
                born_location = author_soup.find('span', class_='author-born-location').get_text(strip=True)
                description = author_soup.find('div', class_='author-description').get_text(strip=True)
                authors[author] = {
                    'fullname': full_name,
                    'born_date': born_date,
                    'born_location': born_location,
                    'description': description
                }
        
        page += 1
    return quotes, authors

quotes_data, authors_data = get_quotes()

# ------------------------ JSON FILES ------------------------

with open('quotes.json', 'w', encoding='utf-8') as f:
    json.dump(quotes_data, f, ensure_ascii=False, indent=4)

with open('authors.json', 'w', encoding='utf-8') as f:
    json.dump(authors_data, f, ensure_ascii=False, indent=4)
    


# ------------------------ MongoDB ------------------------
    
client = MongoClient("mongodb+srv://sgpavlot:lX3ZJFTPWewgcgtm@clustergoit.12fxhyj.mongodb.net/?retryWrites=true&w=majority&appName=ClusterGOIT")
db = client['db-quotes']

# Insert data into collections
db.authors.insert_many(list(authors_data.values()))
db.quotes.insert_many(quotes_data)
    
# ------------------------ PRINT FROM DATABASE ------------------------

# Get all authors and print them
authors = db.authors.find()
for author in authors:
    print(author)

# Get all quotes and print them
quotes = db.quotes.find()
for quote in quotes:
    print(quote)