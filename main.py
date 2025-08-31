import requests
from bs4 import BeautifulSoup
import csv
import time

print("Starting web scraper...")

base_url = "http://quotes.toscrape.com/page/{}/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

all_quotes = []
page = 1

print("Scraping quotes from all pages...")

while True:
    url = base_url.format(page)
    print(f"Scraping page {page}: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to get page {page}, stopping...")
            break
            
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all quote elements on this page
        quotes = soup.find_all('div', class_='quote')
        
        if not quotes:
            print(f"No quotes found on page {page}, reached end of pagination")
            break
            
        print(f"Found {len(quotes)} quotes on page {page}")
        
        # Extract quotes from this page
        for quote in quotes:
            try:
                quote_text = quote.find('span', class_='text').get_text().strip()
                author = quote.find('small', class_='author').get_text().strip()
                tags = [tag.get_text().strip() for tag in quote.find_all('a', class_='tag')]
                
                quote_data = {
                    'text': quote_text,
                    'author': author,
                    'tags': tags,
                    'page': page
                }
                
                all_quotes.append(quote_data)
                print(f"  - {quote_text[:50]}... by {author}")
                
            except AttributeError as e:
                print(f"Error extracting quote on page {page}: {e}")
                continue
        
        page += 1
        
        # Be respectful - add a small delay between requests
        time.sleep(1)
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request to page {page}: {e}")
        break
    except Exception as e:
        print(f"An unexpected error occurred on page {page}: {e}")
        break

print(f"\nScraping completed!")
print(f"Total quotes collected: {len(all_quotes)}")
print(f"Total pages scraped: {page - 1}")

# Display all collected quotes
print("\n" + "="*80)
print("ALL COLLECTED QUOTES:")
print("="*80)

for i, quote in enumerate(all_quotes, 1):
    print(f"\nQuote {i} (Page {quote['page']}):")
    print(f"Text: {quote['text']}")
    print(f"Author: {quote['author']}")
    print(f"Tags: {', '.join(quote['tags'])}")
    print("-" * 60)

# Save results to CSV file
csv_filename = "quotes.csv"
print(f"\nSaving quotes to {csv_filename}...")

try:
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['text', 'author', 'tags', 'page']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each quote as a row
        for quote in all_quotes:
            # Create a copy of the quote dictionary to avoid modifying the original
            quote_copy = quote.copy()
            # This line replaces the 'tags' field in the quote_copy dictionary (which is a shallow copy of the original quote dictionary)
            # with a single string that joins all elements of the quote['tags'] list, separated by commas and a space.
            # For example, if quote['tags'] is ['life', 'inspirational'], then quote_copy['tags'] becomes 'life, inspirational'.
            quote_copy['tags'] = ', '.join(quote['tags'])
            writer.writerow(quote_copy)
    
    print(f"Successfully saved {len(all_quotes)} quotes to {csv_filename}")
    
except Exception as e:
    print(f"Error saving to CSV: {e}")

print("Script completed successfully!")
