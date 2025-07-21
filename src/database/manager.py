# src/database/manager.py

# This module is responsible for all interactions with the local file system,
# specifically for saving and loading our cached data.

import json
import os

def save_to_json(data, file_path):
    """
    Saves a given Python object (like a list or dictionary) to a JSON file.

    Args:
        data: The Python object to save.
        file_path: The path to the file where the data will be saved.
    """
    try:
        # Ensure the directory exists before trying to save the file.
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            # indent=4 makes the JSON file human-readable, which is great for debugging.
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved data to {file_path}")
        return True
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")
        return False

def load_from_json(file_path):
    """
    Loads data from a JSON file into a Python object.

    Args:
        file_path: The path to the file to be loaded.

    Returns:
        The loaded Python object, or None if the file doesn't exist or an error occurs.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded data from {file_path}")
        return data
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return None
