# src/utils.py

# This file contains small, reusable utility functions that can be used
# across different modules of the project.

import time
import random
import config

def randomized_delay():
    """
    Waits for a random amount of time between the minimum and maximum
    delay values specified in the config file. This is crucial for
    making our automated actions appear more human-like.
    """
    delay = random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)
    print(f"Waiting for {delay:.2f} seconds...")
    time.sleep(delay)
