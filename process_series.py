# process_series.py

# This script processes the enriched series data to create a final, validated list
# of series that are confirmed to be in the Mudae bot.

import json
import os
import config # Imports file paths from config.py

def load_nobundles_exception_list():
    """Loads the list of valid series without bundles from nobundles.txt."""
    if not os.path.exists(config.NOBUNDLES_TXT_PATH):
        print(f"Warning: '{config.NOBUNDLES_TXT_PATH}' not found. Proceeding without exception list.")
        return set()
    
    with open(config.NOBUNDLES_TXT_PATH, 'r', encoding='utf-8') as f:
        exceptions = {line.strip() for line in f if line.strip()}
    print(f"Loaded {len(exceptions)} series from the no-bundle exception list.")
    return exceptions

def validate_series_list():
    """
    Loads the enriched series data, validates each series based on bundle presence
    or inclusion in the exception list, and saves the final list.
    """
    print("--- Starting Series Validation Process ---")

    # 1. Load the enriched series data
    try:
        with open(config.ENRICHED_SERIES_DATA_PATH, 'r', encoding='utf-8') as f:
            enriched_list = json.load(f)
        print(f"Successfully loaded {len(enriched_list)} enriched series entries.")
    except FileNotFoundError:
        print(f"ERROR: The file '{config.ENRICHED_SERIES_DATA_PATH}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not read the JSON from '{config.ENRICHED_SERIES_DATA_PATH}'.")
        return

    # 2. Load the exception list
    nobundles_set = load_nobundles_exception_list()

    # 3. Iterate and validate each series
    validated_series = []
    for series in enriched_list:
        # A series is valid if:
        # 1. It has one or more bundles associated with it.
        # OR
        # 2. Its name is in our nobundles.txt exception list.
        
        has_bundles = len(series.get('bundles', [])) > 0
        is_in_exception_list = series.get('name') in nobundles_set

        if has_bundles or is_in_exception_list:
            validated_series.append(series)

    print(f"\nFound {len(validated_series)} valid series that are confirmed to be in the bot.")

    # 4. Save the validated list to a new JSON file
    try:
        with open(config.VALIDATED_SERIES_LIST_PATH, 'w', encoding='utf-8') as f:
            json.dump(validated_series, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved validated series list to '{config.VALIDATED_SERIES_LIST_PATH}'")
    except Exception as e:
        print(f"ERROR: Could not save the validated series file. Reason: {e}")

    print("--- Series Validation Complete ---")

if __name__ == "__main__":
    validate_series_list()
