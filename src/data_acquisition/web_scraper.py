# src/data_acquisition/web_scraper.py

# This module contains the logic for fetching data from the Mudae website.
# It handles both parsing initial HTML and making direct API calls.

import cloudscraper # Use cloudscraper instead of requests to bypass anti-bot measures
import json
from bs4 import BeautifulSoup
import config
from src import utils

# Create a scraper instance. This object will be used for all requests.
# It automatically manages cookies and headers to appear like a real browser.
scraper = cloudscraper.create_scraper()

def get_initial_series_page():
    """
    Fetches the first page of series data by scraping the main search page.
    The data is embedded as a JSON string in a 'data-data' attribute.

    Returns:
        A list of dictionaries, where each dictionary is a series, or None on failure.
    """
    print("Fetching initial series page from HTML...")
    try:
        # Use the scraper object instead of requests.get
        response = scraper.get(config.SERIES_LIST_URL, headers=config.HEADERS)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')
        table_wrapper = soup.find('div', id='table-wrapper')

        if not table_wrapper or 'data-data' not in table_wrapper.attrs:
            print("Error: Could not find the data-data attribute in the HTML.")
            return None

        # The attribute contains a JSON string, so we need to parse it.
        series_data = json.loads(table_wrapper['data-data'])
        print(f"Successfully scraped {len(series_data)} series from the initial page.")
        return series_data

    except Exception as e:
        print(f"An error occurred during the request: {e}")
        return None

def get_api_series_pages():
    """
    Fetches all subsequent pages of series data by making sequential API calls.

    Returns:
        A list of dictionaries containing all series from the API pages.
    """
    all_series = []
    current_page = 1
    
    while True:
        print(f"Fetching series data from API page {current_page}...")
        params = {
            'type': 'series',
            'currentPage': current_page
        }
        try:
            # Use the scraper object for API calls as well
            response = scraper.get(config.API_URL, params=params, headers=config.HEADERS)
            response.raise_for_status()
            data = response.json()

            page_series = data.get('results', [])
            if not page_series:
                print("No more series found on this page. Ending API fetch.")
                break
            
            all_series.extend(page_series)
            print(f"Found {len(page_series)} series on page {current_page}.")

            # If the 'more' flag is false, we know this is the last page.
            if not data.get('more', False):
                print("API indicated this is the last page.")
                break

            current_page += 1
            utils.randomized_delay() # Crucial delay between API calls

        except Exception as e:
            print(f"An error occurred during API request for page {current_page}: {e}")
            break
            
    return all_series

def fetch_master_series_list():
    """
    Orchestrates the fetching of all series, combines them, and filters out bundles.

    Returns:
        A clean list of all individual series.
    """
    initial_series = get_initial_series_page()
    if initial_series is None:
        initial_series = [] # Ensure it's a list even on failure

    utils.randomized_delay() # Wait before starting the API calls

    api_series = get_api_series_pages()

    # Combine both lists and create a master list.
    # We use a dictionary to automatically handle any potential duplicates.
    master_list_dict = {series['idSeries']: series for series in initial_series}
    for series in api_series:
        master_list_dict[series['idSeries']] = series
        
    full_series_list = list(master_list_dict.values())
    print(f"\nTotal unique series/bundles found: {len(full_series_list)}")

    # Filter out entries that are explicitly marked as bundles.
    filtered_list = [
        series for series in full_series_list if not series.get('isBundle', False)
    ]
    print(f"Filtered down to {len(filtered_list)} individual series (removed bundles).")
    
    return filtered_list
