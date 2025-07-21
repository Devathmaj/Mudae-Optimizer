# step3_scrape_bundles.py

# This script is now dedicated to two tasks:
# 1. Validating the series list to ensure all series are in the bot.
# 2. Building a map of which validated series belong to which bundles.

import cloudscraper
from bs4 import BeautifulSoup
import config
from src import utils
from src.database import manager
import urllib.parse
import os

scraper = cloudscraper.create_scraper()

def load_nobundles_exception_list():
    """Loads the list of valid series without bundles from nobundles.txt."""
    if not os.path.exists(config.NOBUNDLES_TXT_PATH):
        print("Warning: nobundles.txt not found. Proceeding without exception list.")
        return set()
    
    with open(config.NOBUNDLES_TXT_PATH, 'r', encoding='utf-8') as f:
        # Read lines and strip whitespace, return as a set for fast lookups.
        exceptions = {line.strip() for line in f if line.strip()}
    print(f"Loaded {len(exceptions)} series from the no-bundle exception list.")
    return exceptions

def main():
    print("--- Running Step 3: Validate Series & Build Bundle Map ---")
    
    # Load the candidate list of series we scraped in Step 1.
    candidate_series_list = manager.load_from_json(config.CANDIDATE_SERIES_LIST_PATH)
    if not candidate_series_list:
        print("Error: Candidate series list not found. Please run 'step1_scrape_series.py' first.")
        return

    # Load the exception list.
    nobundles_set = load_nobundles_exception_list()

    bundle_to_series_map = {}
    validated_series_list = []
    total_series = len(candidate_series_list)
    
    for i, series in enumerate(candidate_series_list):
        series_name = series.get('name')
        series_id = series.get('idSeries')
        
        if not series_name or not series_id:
            continue
            
        # We only want to process actual series, not bundles that might be in the list
        if series.get('isBundle', False):
            continue

        encoded_name = urllib.parse.quote(series_name)
        series_url = f"{config.BASE_URL}/series/{series_id}/{encoded_name}"
        
        print(f"({i+1}/{total_series}) Processing: {series_name}")
        
        try:
            response = scraper.get(series_url, headers=config.HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the "Bundles" section on the page
            bundles_section = soup.find('section', id='series')
            
            # --- The New Validation Logic ---
            is_valid = False
            if bundles_section:
                is_valid = True
            elif series_name in nobundles_set:
                is_valid = True
                print(f"  -> Found in nobundles.txt. Marking as valid.")

            if is_valid:
                validated_series_list.append(series) # Add the series to our final clean list
                
                # If the bundles section exists, process it
                if bundles_section:
                    bundle_links = bundles_section.find_all('a', class_='series-name')
                    for link in bundle_links:
                        bundle_name = link.get_text(strip=True)
                        if bundle_name not in bundle_to_series_map:
                            bundle_to_series_map[bundle_name] = []
                        bundle_to_series_map[bundle_name].append(series_name)
            else:
                print(f"  -> No bundles section and not in exception list. Skipping as invalid.")

            utils.randomized_delay()

        except Exception as e:
            print(f"  - Could not process series {series_name}. Error: {e}")
            utils.randomized_delay()

    print(f"\nValidated {len(validated_series_list)} series as being in the bot.")
    print(f"Found {len(bundle_to_series_map)} unique bundles from validated series.")
    
    # Save the two outputs
    manager.save_to_json(validated_series_list, config.VALIDATED_SERIES_LIST_PATH)
    manager.save_to_json(bundle_to_series_map, config.BUNDLE_TO_SERIES_MAP_PATH)
    print("--- Step 3 Complete ---")

if __name__ == "__main__":
    main()
