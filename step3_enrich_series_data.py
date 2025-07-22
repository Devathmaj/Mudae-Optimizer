# step3_enrich_series_data.py

# This script enriches the series data collected in Step 1.
# It visits each series page and scrapes two additional pieces of information:
# 1. A list of all characters belonging to that series.
# 2. A list of all bundles that the series is a part of.
# It saves progress on error and can resume from where it left off.

import cloudscraper
from bs4 import BeautifulSoup
import config
from src import utils
from src.database import manager
import urllib.parse
import os
import sys # Import sys to allow for script termination

scraper = cloudscraper.create_scraper()

if config.PROXY:
    print("Using proxy configuration...")
    scraper.proxies.update(config.PROXY)

def main():
    print("--- Running Step 3: Enrich Series Data with Characters and Bundles ---")
    
    # Load the master list of series we scraped in Step 1.
    master_series_list = manager.load_from_json(config.MASTER_SERIES_LIST_PATH)
    if not master_series_list:
        print(f"Error: Master series list not found at '{config.MASTER_SERIES_LIST_PATH}'.")
        print("Please run 'step1_scrape_series.py' first.")
        return

    # --- Resume Logic ---
    # Check if a partial data file already exists.
    enriched_data = []
    processed_series_ids = set()
    if os.path.exists(config.ENRICHED_SERIES_DATA_PATH):
        print("Partial data file found. Loading progress...")
        # Use a default empty list if the file is empty or corrupted
        enriched_data = manager.load_from_json(config.ENRICHED_SERIES_DATA_PATH) or []
        if enriched_data:
            # Create a set of IDs for series we have already processed for fast lookups.
            processed_series_ids = {series['idSeries'] for series in enriched_data}
            print(f"Resuming. {len(processed_series_ids)} series have already been processed.")
    # --------------------

    # --- FOR TESTING: Process only the first 20 series ---
    # To run the full script on all series, comment out or delete the following line.
    # master_series_list = master_series_list[:20]
    # ----------------------------------------------------

    total_series = len(master_series_list)
    
    for i, series in enumerate(master_series_list):
        series_name = series.get('name')
        series_id = series.get('idSeries')
        
        # --- Resume Check ---
        if series_id in processed_series_ids:
            continue # Skip this series as it's already in our save file.
        # --------------------

        if not series_name or not series_id or series.get('isBundle', False):
            continue

        # URL encode the series name, ensuring that slashes ('/') are also encoded.
        encoded_name = urllib.parse.quote(series_name, safe='')
        primary_series_url = f"{config.BASE_URL}/series/{series_id}/{encoded_name}"
        fallback_series_url = f"{config.BASE_URL}/series/{series_id}"
        
        print(f"({i+1}/{total_series}) Processing: {series_name}")
        
        try:
            try:
                response = scraper.get(primary_series_url, headers=config.HEADERS)
                response.raise_for_status()
            except Exception:
                print(f"  - Primary URL failed for {series_name}. Trying fallback URL.")
                response = scraper.get(fallback_series_url, headers=config.HEADERS)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            bundle_list = []
            bundles_section = soup.find('section', id='series')
            if bundles_section:
                bundle_links = bundles_section.find_all('a', class_='series-name')
                for link in bundle_links:
                    bundle_list.append(link.get_text(strip=True))
            
            character_list = []
            characters_section = soup.find('section', id='characters')
            if characters_section:
                char_elements = characters_section.find_all('li', class_='character')
                for char_element in char_elements:
                    name_tag = char_element.find('a', class_='name')
                    if name_tag:
                        character_list.append(name_tag.get_text(strip=True))

            enriched_series_entry = series.copy()
            enriched_series_entry['bundles'] = bundle_list
            enriched_series_entry['characters'] = character_list
            
            enriched_data.append(enriched_series_entry)
            
            utils.randomized_delay()

        except Exception as e:
            # --- Save Progress on Error ---
            print(f"\nCRITICAL ERROR: Could not process series {series_name}. Error: {e}")
            print("Saving progress before shutting down...")
            manager.save_to_json(enriched_data, config.ENRICHED_SERIES_DATA_PATH)
            print(f"Progress saved. {len(enriched_data)} series have been processed.")
            print("Shutting down.")
            sys.exit(1) # Exit immediately
            # ----------------------------

    print(f"\nSuccessfully enriched data for {len(enriched_data)} series.")
    
    # Save the final, complete data to a single file
    manager.save_to_json(enriched_data, config.ENRICHED_SERIES_DATA_PATH)
    print(f"Enriched data saved to '{config.ENRICHED_SERIES_DATA_PATH}'")
    print("--- Step 3 Complete ---")

if __name__ == "__main__":
    main()
