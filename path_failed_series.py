# patch_failed_series.py

# This script is a utility to fix an existing enriched_series_data_copy.json file.
# It reads a character validation log to identify failed series, and re-scrapes
# them using an existing browser session cookie for authentication.

import cloudscraper
from bs4 import BeautifulSoup
import config
from src import utils
from src.database import manager
import urllib.parse
import os
import sys
import json

# --- Authentication ---
# This script no longer uses username/password. Instead, it will ask for your
# session cookie to use your existing logged-in browser session.
# --------------------

def get_session_cookie():
    """
    Prompts the user to enter their session cookie.
    
    Instructions for the user:
    1. Log in to mudae.net in your web browser.
    2. Open the Developer Tools (usually by pressing F12).
    3. Go to the 'Application' (in Chrome) or 'Storage' (in Firefox) tab.
    4. On the left side, find 'Cookies' and click on the 'https://mudae.net' entry.
    5. Find the cookie named 'connect.sid'.
    6. Copy the long string from the 'Value' column.
    7. Paste it into the terminal when prompted.
    """
    print("\n--- Please provide your session cookie ---")
    print("See the instructions in the script's comments for how to find it.")
    cookie_value = input("Paste your 'connect.sid' cookie value here and press Enter: ")
    if not cookie_value:
        print("ERROR: Cookie value cannot be empty. Exiting.")
        sys.exit(1)
    return f"connect.sid={cookie_value}"

def main():
    print("--- Running Patch Script for Failed Series ---")

    # 1. Load the log file to find which series failed
    try:
        with open(config.CHARACTER_VALIDATION_LOG_PATH, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        # Create a unique set of series that need to be fixed
        series_to_fix_names = {entry['character']['series'] for entry in log_data}
        print(f"Found {len(series_to_fix_names)} unique series to fix from the log file.")
    except FileNotFoundError:
        print(f"ERROR: The log file '{config.CHARACTER_VALIDATION_LOG_PATH}' was not found.")
        return

    # 2. Load the enriched data file that we need to patch
    enriched_data = manager.load_from_json(config.ENRICHED_SERIES_DATA_COPY_PATH)
    if not enriched_data:
        print(f"ERROR: Could not load data from '{config.ENRICHED_SERIES_DATA_COPY_PATH}'.")
        return

    # Create a dictionary for easy access to update the series data
    enriched_data_map = {series['idSeries']: series for series in enriched_data}
    
    # Create a name-to-ID map to find the series from the log
    name_to_id_map = {series['name']: series['idSeries'] for series in enriched_data}

    # 3. Get session cookie and create an authenticated scraper
    session_cookie = get_session_cookie()
    scraper = cloudscraper.create_scraper()
    # Add the cookie to all subsequent requests made by this scraper instance
    scraper.headers.update({'Cookie': session_cookie})

    # List to keep track of series that failed with non-critical errors
    skipped_series = []

    # 4. Loop through only the failed series and re-scrape them
    for i, series_name in enumerate(series_to_fix_names):
        series_id = name_to_id_map.get(series_name)
        if not series_id:
            print(f"Warning: Could not find ID for series '{series_name}'. Skipping.")
            skipped_series.append(f"{series_name} (Reason: ID not found in enriched data)")
            continue

        print(f"({i+1}/{len(series_to_fix_names)}) Fixing: {series_name}")
        
        encoded_name = urllib.parse.quote(series_name, safe='')
        series_url = f"{config.BASE_URL}/series/{series_id}/{encoded_name}"
        
        try:
            response = scraper.get(series_url)
            # This will raise an HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            bundle_list = []
            if bundles_section := soup.find('section', id='series'):
                for link in bundles_section.find_all('a', class_='series-name'):
                    bundle_list.append(link.get_text(strip=True))

            character_list = []
            if characters_section := soup.find('section', id='characters'):
                for char_element in characters_section.find_all('li', class_='character'):
                    if name_tag := char_element.find('a', class_='name'):
                        character_list.append(name_tag.get_text(strip=True))

            # Update the entry in our map with the new, correct data
            if series_id in enriched_data_map:
                enriched_data_map[series_id]['bundles'] = bundle_list
                enriched_data_map[series_id]['characters'] = character_list
            
            utils.randomized_delay()

        except cloudscraper.exceptions.CloudflareException as e:
            # Check for critical status codes that indicate a ban or rate limit
            if e.response.status_code == 403 or e.response.status_code == 429:
                print(f"\nCRITICAL ERROR: Received status code {e.response.status_code} for {series_name}.")
                print("This indicates a potential IP ban or rate limit. Shutting down immediately.")
                sys.exit(1)
            else:
                # Handle other, non-critical errors by skipping
                print(f"  - FAILED to fix {series_name}. Error: {e}. Skipping this series.")
                skipped_series.append(f"{series_name} (Reason: {e})")
                utils.randomized_delay()
                continue
        except Exception as e:
            # Catch any other general errors (e.g., timeouts)
            print(f"  - FAILED to fix {series_name}. Error: {e}. Skipping this series.")
            skipped_series.append(f"{series_name} (Reason: {e})")
            utils.randomized_delay()
            continue

    # 5. Convert the map back to a list and save it, overwriting the original file
    fixed_list = list(enriched_data_map.values())
    manager.save_to_json(fixed_list, config.ENRICHED_SERIES_DATA_COPY_PATH)
    
    print("\n--- Patching Complete ---")
    print(f"The file '{config.ENRICHED_SERIES_DATA_COPY_PATH}' has been updated in place.")
    
    # 6. Print the final report of any skipped series
    if skipped_series:
        print("\nThe following series were skipped due to non-critical errors:")
        for item in skipped_series:
            print(f"  - {item}")
    
    print("\nYou should now re-run the 'validate_characters.py' script.")

if __name__ == "__main__":
    main()
