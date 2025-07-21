# config.py

# This file contains the configuration settings for the Mudae Optimizer bot.
# Centralizing configuration makes the bot easier to manage and modify.

# --- Web Scraper Configuration ---
BASE_URL = "https://mudae.net"
SERIES_LIST_URL = f"{BASE_URL}/search?type=series"
CHARACTER_LIST_URL = f"{BASE_URL}/search?type=character"
API_URL = f"{BASE_URL}/api/search"

# Headers to mimic a real browser visit.
# Using a common User-Agent is important to avoid being blocked.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# --- Proxy Configuration ---
# To run the scraper through a different IP address.
# TO RUN WITHOUT A PROXY: Leave this dictionary empty, exactly as it is below.
# The script will automatically detect that it's empty and run on your own network.
#
# TO USE A PROXY: Uncomment and fill in your proxy details.
# Format: "http://username:password@host:port" or "http://host:port"
PROXY = {
    # "http": "http://your_proxy_address:port",
    # "https": "http://your_proxy_address:port",
}

# --- Data File Paths ---
# Defines where the collected data will be stored.
DATA_DIR = "data"
# Step 1 now produces a candidate list.
CANDIDATE_SERIES_LIST_PATH = f"{DATA_DIR}/candidate_series_list.json"
MASTER_CHARACTER_LIST_PATH = f"{DATA_DIR}/master_character_list.json"
BUNDLE_TO_SERIES_MAP_PATH = f"{DATA_DIR}/bundle_to_series_map.json"
# Step 3 will produce the final, validated list.
VALIDATED_SERIES_LIST_PATH = f"{DATA_DIR}/validated_master_series_list.json"

# --- Exception File ---
# The list of valid series that have no bundles.
NOBUNDLES_TXT_PATH = "nobundles.txt"


# --- Delays for Mimicking Human Behavior ---
# Using randomized delays is crucial to mitigate the risk of detection.
# Values are in seconds.
REQUEST_DELAY_MIN = 1.0
REQUEST_DELAY_MAX = 2.0
