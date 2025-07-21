# step2_scrape_characters.py

# This script is dedicated to Step 2: Fetching the master list of all characters.
# It now also identifies characters with duplicate names and saves them to a separate file.
# UPDATE: Added immediate shutdown on any network error to prevent IP bans.

import cloudscraper
import json
from bs4 import BeautifulSoup
import config
from src import utils
from src.database import manager
from collections import defaultdict
import sys # Import sys to allow for script termination

scraper = cloudscraper.create_scraper()

def get_initial_page(url):
    """Fetches the first page of data by scraping the main search page."""
    print(f"Fetching initial page from HTML: {url}")
    try:
        response = scraper.get(url, headers=config.HEADERS)
        response.raise_for_status() # This will raise an exception for HTTP errors (like 403, 429)
        soup = BeautifulSoup(response.text, 'html.parser')
        table_wrapper = soup.find('div', id='table-wrapper')
        if not table_wrapper or 'data-data' not in table_wrapper.attrs:
            print("CRITICAL ERROR: Could not find the data-data attribute in the HTML.")
            sys.exit(1) # Exit immediately
        data = json.loads(table_wrapper['data-data'])
        print(f"Successfully scraped {len(data)} items from the initial page.")
        return data
    except Exception as e:
        # If any error occurs (network, parsing, etc.), print it and shut down.
        print(f"\nCRITICAL ERROR: An error occurred during the initial page request: {e}")
        print("Shutting down immediately to prevent further requests.")
        sys.exit(1) # Exit immediately

def get_api_pages(item_type):
    """Fetches all subsequent pages of data from the API."""
    all_items = []
    current_page = 1
    while True:
        print(f"Fetching {item_type} data from API page {current_page}...")
        params = {'type': item_type, 'currentPage': current_page}
        try:
            response = scraper.get(config.API_URL, params=params, headers=config.HEADERS)
            response.raise_for_status() # This will raise an exception for HTTP errors
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
            # If any error occurs, print it and shut down the entire script.
            print(f"\nCRITICAL ERROR: An error occurred during API request for page {current_page}: {e}")
            print("Shutting down immediately to prevent further requests.")
            sys.exit(1) # Exit immediately
    return all_items

def main():
    print("--- Running Step 2: Fetch Master Character List ---")
    initial_chars = get_initial_page(config.CHARACTER_LIST_URL)
    utils.randomized_delay()
    api_chars = get_api_pages('character')
    
    master_list_dict = {char['idChar']: char for char in initial_chars}
    for char in api_chars:
        master_list_dict[char['idChar']] = char
        
    full_list = list(master_list_dict.values())
    print(f"\nTotal unique characters found: {len(full_list)}")
    
    # --- New Logic to Find Duplicates ---
    names_to_chars = defaultdict(list)
    for char in full_list:
        # Group all characters by their name
        names_to_chars[char['name']].append(char)
    
    # Find all names that appear more than once
    duplicates = {name: chars for name, chars in names_to_chars.items() if len(chars) > 1}
    
    print(f"Found {len(duplicates)} character names that are used more than once.")
    
    # Save the master list and the duplicates list
    manager.save_to_json(full_list, config.MASTER_CHARACTER_LIST_PATH)
    manager.save_to_json(duplicates, config.DUPLICATE_CHARACTERS_PATH)
    print("--- Step 2 Complete ---")

if __name__ == "__main__":
    main()
