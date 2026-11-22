"""
ResourcesNow - Phase 3 Optimized Resource Locator
Core engine using a dictionary catalog, Euclidean GPS distance math,
bounded LRU caching, and in-place Randomized Quicksort.
"""

import math
import random
from functools import lru_cache

# Supported walkable presets (in miles) and default sample user location
WALKABLE_PRESETS = (0.5, 1.5)
DEFAULT_USER_LAT = 40.0000
DEFAULT_USER_LON = -76.0000

# Empty dictionary catalog populated dynamically.
# Each resource is stored as a (name, lat, lon) tuple to keep memory usage low.
RESOURCE_CATALOG = {}


def calculate_distance(user_lat, user_lon, resource_lat, resource_lon):
    """Calculates straight-line Euclidean distance in miles (Maria et al., 2020)."""
    if user_lat < -90 or user_lat > 90 or user_lon < -180 or user_lon > 180:
        raise ValueError("Invalid user GPS coordinates.")
    if resource_lat < -90 or resource_lat > 90 or resource_lon < -180 or resource_lon > 180:
        raise ValueError("Invalid resource GPS coordinates.")

    lat_diff = resource_lat - user_lat
    lon_diff = resource_lon - user_lon
    degree_distance = math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
    miles = degree_distance * 69.0
    return round(miles, 4)


def partition(arr, low, high):
    """Picks a random pivot and moves smaller (distance, name) tuples to the left."""
    pivot_index = random.randint(low, high)
    arr[pivot_index], arr[high] = arr[high], arr[pivot_index]
    pivot = arr[high]

    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quicksort_in_place(arr, low, high):
    """Recursively sorts the list in place using Randomized Quicksort."""
    if low < high:
        pivot_pos = partition(arr, low, high)
        quicksort_in_place(arr, low, pivot_pos - 1)
        quicksort_in_place(arr, pivot_pos + 1, high)


def quicksort_resources(resource_tuples):
    """Checks for negative distances, then sorts (distance, name) tuples in place."""
    for item in resource_tuples:
        dist = item[0]
        name = item[1]
        if dist < 0:
            raise ValueError(
                f"GPS calculation error: negative distance ({dist} mi) for {name}."
            )

    if len(resource_tuples) > 1:
        quicksort_in_place(resource_tuples, 0, len(resource_tuples) - 1)

    return resource_tuples


@lru_cache(maxsize=64)
def cached_search(categories_tuple, rounded_lat, rounded_lon, max_radius):
    """Filters by distance, sorts matches, and caches up to 64 recent queries."""
    walkable_matches = []
    fallbacks = []

    for category in categories_tuple:
        if category not in RESOURCE_CATALOG:
            continue

        entry = RESOURCE_CATALOG[category]
        category_matches = []

        for resource in entry["resources"]:
            name = resource[0]
            resource_lat = resource[1]
            resource_lon = resource[2]

            dist = calculate_distance(rounded_lat, rounded_lon, resource_lat, resource_lon)
            if dist <= max_radius:
                category_matches.append((dist, name))

        if len(category_matches) > 0:
            walkable_matches.extend(category_matches)
        else:
            fallbacks.append(entry["fallback"])

    if len(walkable_matches) > 0:
        quicksort_resources(walkable_matches)

    return tuple(walkable_matches), tuple(fallbacks)


def find_walkable_resources(
    user_categories,
    user_lat=DEFAULT_USER_LAT,
    user_lon=DEFAULT_USER_LON,
    max_radius=1.5,
):
    """Validates inputs, rounds GPS coordinates, and calls the cached search."""
    if max_radius <= 0:
        raise ValueError("Invalid max_radius: must be greater than 0.")
    if user_lat < -90 or user_lat > 90 or user_lon < -180 or user_lon > 180:
        raise ValueError("Invalid user GPS coordinates.")

    # Remove duplicate categories and convert to a sorted tuple for @lru_cache
    unique_categories = set(user_categories)
    sorted_categories = sorted(unique_categories)
    categories_tuple = tuple(sorted_categories)

    # Round GPS coordinates to 3 decimal places (~0.07 mi) for better cache hits
    rounded_lat = round(user_lat, 3)
    rounded_lon = round(user_lon, 3)

    results, fallbacks = cached_search(
        categories_tuple, rounded_lat, rounded_lon, max_radius
    )
    return list(results), list(fallbacks)


def add_resource(category, name, resource_lat, resource_lon, fallback=None):
    """Adds a new (name, lat, lon) resource tuple to the catalog and clears the cache."""
    if resource_lat < -90 or resource_lat > 90 or resource_lon < -180 or resource_lon > 180:
        raise ValueError("Invalid resource GPS coordinates.")

    if category not in RESOURCE_CATALOG:
        if fallback is None:
            fallback = f"No walkable {category} nearby. Contact: Local Helpline (211)"
        RESOURCE_CATALOG[category] = {
            "resources": [],
            "fallback": fallback,
        }

    RESOURCE_CATALOG[category]["resources"].append((name, resource_lat, resource_lon))
    cached_search.cache_clear()