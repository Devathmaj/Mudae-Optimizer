# validate_characters.py

# This script performs the final, most important validation of the character list.
# It cross-references the master character list with the validated series list
# to ensure every character actually exists within their specified series in the bot.
# UPDATE: Added logging to track and save all discarded characters for debugging.

import json
import os
import re
import config # Imports file paths from config.py

def normalize_character_name(name):
    """
    Removes the {series_abbreviation} part from a character's name for comparison.
    For example, 'Rem {DN}' becomes 'Rem'.
    """
    return re.sub(r'\s*\{.*?\}\s*$', '', name).strip()

def create_series_character_lookup(validated_series_list):
    """
    Creates a highly efficient lookup structure from the validated series list.
    Returns a dictionary mapping: {series_name: {set_of_character_names}}
    """
    lookup = {}
    for series in validated_series_list:
        if 'name' in series and 'characters' in series:
            # Using a set for character names provides nearly instant lookups.
            lookup[series['name']] = set(series['characters'])
    return lookup

def validate_characters():
    """
    Loads both datasets, cross-verifies each character, and saves the final list.
    """
    print("--- Starting Character Validation Process ---")

    # 1. Load the master character list (from step2)
    try:
        with open(config.MASTER_CHARACTER_LIST_PATH, 'r', encoding='utf-8') as f:
            master_characters = json.load(f)
        print(f"Loaded {len(master_characters)} characters from '{config.MASTER_CHARACTER_LIST_PATH}'")
    except FileNotFoundError:
        print(f"ERROR: The file '{config.MASTER_CHARACTER_LIST_PATH}' was not found.")
        return

    # 2. Load the validated series list (from process_series.py)
    try:
        with open(config.VALIDATED_SERIES_LIST_PATH, 'r', encoding='utf-8') as f:
            validated_series = json.load(f)
        print(f"Loaded {len(validated_series)} validated series from '{config.VALIDATED_SERIES_LIST_PATH}'")
    except FileNotFoundError:
        print(f"ERROR: The file '{config.VALIDATED_SERIES_LIST_PATH}' was not found.")
        print("Please run 'process_series.py' first.")
        return

    # 3. Create the efficient lookup table
    series_lookup = create_series_character_lookup(validated_series)
    print("Created series-to-character lookup table for fast verification.")

    # 4. Iterate and validate each character
    final_character_list = []
    discarded_log = [] # List to store discarded characters and the reason
    for character in master_characters:
        char_name = character.get('name')
        char_series = character.get('series')

        if not char_name or not char_series:
            discarded_log.append({
                "character": character,
                "reason": "Missing name or series field"
            })
            continue

        normalized_name = normalize_character_name(char_name)

        # Check if the character's series exists in our validated list
        if char_series in series_lookup:
            # Check if the normalized character name is in that series' character set
            if normalized_name in series_lookup[char_series]:
                final_character_list.append(character)
            else:
                # Reason 1: Character name not found within the correct series
                discarded_log.append({
                    "character": character,
                    "reason": "Character name not found in series roster"
                })
        else:
            # Reason 2: The series name itself was not found in the validated list
            discarded_log.append({
                "character": character,
                "reason": "Series not found in validated list"
            })

    print(f"\nValidation complete. Found {len(final_character_list)} characters that exist in the bot.")
    print(f"Discarded {len(discarded_log)} characters. See log for details.")

    # 5. Save the final, validated list of characters
    try:
        with open(config.VALIDATED_CHARACTER_LIST_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_character_list, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved validated character list to '{config.VALIDATED_CHARACTER_LIST_PATH}'")
    except Exception as e:
        print(f"ERROR: Could not save the validated character file. Reason: {e}")

    # 6. Save the log of discarded characters for debugging
    try:
        with open(config.CHARACTER_VALIDATION_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(discarded_log, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved discard log to '{config.CHARACTER_VALIDATION_LOG_PATH}'")
    except Exception as e:
        print(f"ERROR: Could not save the discard log file. Reason: {e}")

    print("--- Character Validation Complete ---")

if __name__ == "__main__":
    validate_characters()
