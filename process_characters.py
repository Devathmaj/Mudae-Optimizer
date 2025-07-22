# process_characters.py

# This script processes the master character list to identify duplicates.
# It reads 'master_character_list.json', finds all characters that share
# the exact same name, and saves these groups into a new file.

import json
from collections import defaultdict
import config # Imports file paths from config.py

def find_and_save_duplicates():
    """
    Loads the master character list, finds duplicates by name, and saves them.
    """
    print("--- Starting Duplicate Character Check ---")

    # 1. Load the existing master character list
    try:
        with open(config.MASTER_CHARACTER_LIST_PATH, 'r', encoding='utf-8') as f:
            all_characters = json.load(f)
        print(f"Successfully loaded {len(all_characters)} characters from '{config.MASTER_CHARACTER_LIST_PATH}'")
    except FileNotFoundError:
        print(f"ERROR: The file '{config.MASTER_CHARACTER_LIST_PATH}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not read the JSON from '{config.MASTER_CHARACTER_LIST_PATH}'.")
        return

    # 2. Group all characters by their 'name' field
    names_to_chars = defaultdict(list)
    for char in all_characters:
        if 'name' in char:
            names_to_chars[char['name']].append(char)

    # 3. Filter to find names that appear more than once
    duplicates = {name: chars for name, chars in names_to_chars.items() if len(chars) > 1}

    if not duplicates:
        print("No duplicate character names were found.")
        print("--- Duplicate Check Complete ---")
        return

    print(f"\nFound {len(duplicates)} character names that are used by multiple characters.")

    # 4. Save the groups of duplicates to a new JSON file
    try:
        with open(config.DUPLICATE_CHARACTERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(duplicates, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved duplicate characters to '{config.DUPLICATE_CHARACTERS_PATH}'")
    except Exception as e:
        print(f"ERROR: Could not save the duplicates file. Reason: {e}")

    print("--- Duplicate Check Complete ---")

if __name__ == "__main__":
    find_and_save_duplicates()
