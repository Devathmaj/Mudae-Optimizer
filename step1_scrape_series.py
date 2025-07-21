# step1_scrape_series.py

# This script is dedicated to Step 1: Fetching the master list of all series.
# It can be run independently to complete this specific task.

import cloudscraper
import json
from bs4 import BeautifulSoup
import config
from src import utils
from src.database import manager

# Create a scraper instance for all requests
scraper = cloudscraper.create_scraper()

def get_initial_page(url):
    """Fetches the first page of data by scraping the main search page."""
    print(f"Fetching initial page from HTML: {url}")
    try:
        response = scraper.get(url, headers=config.HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table_wrapper = soup.find('div', id='table-wrapper')
        if not table_wrapper or 'data-data' not in table_wrapper.attrs:
            print("Error: Could not find the data-data attribute.")
            return None
        data = json.loads(table_wrapper['data-data'])
        print(f"Successfully scraped {len(data)} items from the initial page.")
        return data
    except Exception as e:
        print(f"An error occurred during the initial page request: {e}")
        return None

def get_api_pages(item_type):
    """Fetches all subsequent pages of data from the API."""
    all_items = []
    current_page = 1
    while True:
        print(f"Fetching {item_type} data from API page {current_page}...")
        params = {'type': item_type, 'currentPage': current_page}
        try:
            response = scraper.get(config.API_URL, params=params, headers=config.HEADERS)
            response.raise_for_status()
            data = response.json()
            page_items = data.get('results', [])
            if not page_items:
                print("No more items found. Ending API fetch.")
                break
            all_items.extend(page_items)
            print(f"Found {len(page_items)} {item_type} on page {current_page}.")
            if not data.get('more', False):
                print("API indicated this is the last page.")
                break
            current_page += 1
            utils.randomized_delay()
        except Exception as e:
            print(f"An error occurred during API request for page {current_page}: {e}")
            break
    return all_items

def main():
    print("--- Running Step 1: Fetch Master Series List ---")
    initial_series = get_initial_page(config.SERIES_LIST_URL) or []
    utils.randomized_delay()
    api_series = get_api_pages('series')
    
    master_list_dict = {series['idSeries']: series for series in initial_series}
    for series in api_series:
        master_list_dict[series['idSeries']] = series
        
    full_list = list(master_list_dict.values())
    print(f"\nTotal unique series/bundles found: {len(full_list)}")
    
    filtered_list = [s for s in full_list if not s.get('isBundle', False)]
    print(f"Filtered down to {len(filtered_list)} individual series.")
    
    manager.save_to_json(filtered_list, config.MASTER_SERIES_LIST_PATH)
    print("--- Step 1 Complete ---")

if __name__ == "__main__":
    main()
