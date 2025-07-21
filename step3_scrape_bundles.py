# step3_scrape_bundles.py

# This script is dedicated to Step 3: Building a map of which series belong to which bundles.
# It reads the master series list, then visits each series page to find this information.

import cloudscraper
from bs4 import BeautifulSoup
import config
from src import utils
from src.database import manager
import urllib.parse

scraper = cloudscraper.create_scraper()

def main():
    print("--- Running Step 3: Build Bundle-to-Series Map ---")
    
    # First, load the master list of series we already scraped.
    master_series_list = manager.load_from_json(config.MASTER_SERIES_LIST_PATH)
    if not master_series_list:
        print("Error: Master series list not found. Please run 'step1_scrape_series.py' first.")
        return

    bundle_to_series_map = {}
    total_series = len(master_series_list)
    
    for i, series in enumerate(master_series_list):
        series_name = series.get('name')
        series_id = series.get('idSeries')
        
        if not series_name or not series_id:
            continue

        # URL encode the series name to handle special characters
        encoded_name = urllib.parse.quote(series_name)
        series_url = f"{config.BASE_URL}/series/{series_id}/{encoded_name}"
        
        print(f"({i+1}/{total_series}) Scraping bundles for: {series_name}")
        
        try:
            response = scraper.get(series_url, headers=config.HEADERS)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the "Bundles" section on the page
            bundles_section = soup.find('section', id='series')
            if bundles_section:
                bundle_links = bundles_section.find_all('a', class_='series-name')
                for link in bundle_links:
                    bundle_name = link.get_text(strip=True)
                    
                    # Add the series to this bundle's list in our map
                    if bundle_name not in bundle_to_series_map:
                        bundle_to_series_map[bundle_name] = []
                    bundle_to_series_map[bundle_name].append(series_name)
            
            utils.randomized_delay()

        except Exception as e:
            print(f"  - Could not process series {series_name}. Error: {e}")
            utils.randomized_delay() # Still wait to avoid spamming on errors

    print(f"\nFound {len(bundle_to_series_map)} unique bundles.")
    manager.save_to_json(bundle_to_series_map, config.BUNDLE_TO_SERIES_MAP_PATH)
    print("--- Step 3 Complete ---")

if __name__ == "__main__":
    main()
