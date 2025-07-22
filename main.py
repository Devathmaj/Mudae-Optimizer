# main.py

# This is the main entry point for the Mudae Optimizer bot.
# It acts as a launcher to run the different data scraping steps independently.

import sys

# We import the main functions from our new standalone scripts
# NOTE: Filenames cannot start with numbers in Python for imports.
# The script files have been renamed (e.g., '1_scrape_series.py' -> 'step1_scrape_series.py')
import step1_scrape_series
import step2_scrape_characters
import step3_enrich_series_data

def main():
    """
    Provides a simple command-line interface to run the different scraping scripts.
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <step>")
        print("Available steps: series, characters, bundles")
        return

    step = sys.argv[1].lower()

    if step == "series":
        step1_scrape_series.main()
    elif step == "characters":
        step2_scrape_characters.main()
    elif step == "bundles":
        step3_enrich_series_data.main()
    else:
        print(f"Error: Unknown step '{step}'.")
        print("Available steps: series, characters, bundles")

if __name__ == "__main__":
    main()
