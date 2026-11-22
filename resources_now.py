"""
ResourcesNow - Phase 3 Optimized Resource Locator
Core engine using dictionary indexing, Euclidean GPS distance calculation,
bounded LRU caching, and in-place Randomized Quicksort.
"""

import math
import random
from functools import lru_cache

# Supported walkable distance presets (in miles)
WALKABLE_PRESETS = (0.5, 1.5)

# Default sample user location (latitude, longitude)
DEFAULT_USER_LOCATION = (40.0000, -76.0000)

# Empty dictionary-backed catalog populated dynamically via add_resource()
# or data_generator.py. Stores immutable (name, lat, lon) tuples to save RAM.
RESOURCE_CATALOG = {}


def validate_coordinates(lat, lon):
    """Validates that latitude and longitude fall within standard GPS ranges."""
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        raise ValueError(f"GPS calculation error: invalid coordinates ({lat}, {lon}).")


def calculate_distance(user_lat, user_lon, fac_lat, fac_lon):
    """
    Calculates straight-line Euclidean distance in miles between two GPS points
    using the degree-to-mile conversion (1 degree ~= 69 miles) from Maria et al. (2020).
    """
    validate_coordinates(user_lat, user_lon)
    validate_coordinates(fac_lat, fac_lon)
    degree_distance = math.sqrt((fac_lat - user_lat) ** 2 + (fac_lon - user_lon) ** 2)
    return round(degree_distance * 69.0, 4)


def _partition(arr, low, high):
    """Partitions (distance, name) tuples in place using a randomized pivot."""
    pivot_index = random.randint(low, high)
    arr[pivot_index], arr[high] = arr[high], arr[pivot_index]
    pivot = arr[high]

    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def _quicksort_in_place(arr, low, high):
    """Recursively sorts the array in place using Randomized Quicksort."""
    if low < high:
        pivot_pos = _partition(arr, low, high)
        _quicksort_in_place(arr, low, pivot_pos - 1)
        _quicksort_in_place(arr, pivot_pos + 1, high)


def quicksort_resources(resource_tuples):
    """
    Validates distances and sorts (distance, name) tuples in ascending order
    using in-place Randomized Quicksort.
    """
    for dist, name in resource_tuples:
        if dist < 0:
            raise ValueError(
                f"GPS calculation error: negative distance ({dist} mi) for {name}."
            )

    if len(resource_tuples) > 1:
        _quicksort_in_place(resource_tuples, 0, len(resource_tuples) - 1)
    return resource_tuples


@lru_cache(maxsize=64)
def cached_search(normalized_categories, rounded_lat, rounded_lon, max_radius):
    """
    Cached query engine for repeat searches within the same rounded GPS grid cell.
    Returns immutable tuples so cached entries cannot be mutated by callers.
    """
    walkable_matches = []
    fallbacks = []

    for category in normalized_categories:
        entry = RESOURCE_CATALOG.get(category)
        if entry is None:
            continue

        category_matches = []
        for name, fac_lat, fac_lon in entry["resources"]:
            dist = calculate_distance(rounded_lat, rounded_lon, fac_lat, fac_lon)
            if dist <= max_radius:
                category_matches.append((dist, name))

        if category_matches:
            walkable_matches.extend(category_matches)
        else:
            fallbacks.append(entry["fallback"])

    if walkable_matches:
        quicksort_resources(walkable_matches)

    return tuple(walkable_matches), tuple(fallbacks)


def find_walkable_resources(
    user_categories,
    user_lat=DEFAULT_USER_LOCATION[0],
    user_lon=DEFAULT_USER_LOCATION[1],
    max_radius=1.5,
):
    """
    Finds and sorts walkable resources within max_radius miles of the user's GPS coordinates.
    Rounds coordinates to 3 decimal places (~0.07 mi) to improve LRU cache hit rates.
    """
    if max_radius <= 0:
        raise ValueError("Invalid max_radius: must be greater than 0.")
    validate_coordinates(user_lat, user_lon)

    # Deduplicate and sort categories so equivalent requests share the same cache key
    normalized_categories = tuple(sorted(set(user_categories)))
    rounded_lat = round(user_lat, 3)
    rounded_lon = round(user_lon, 3)

    results, fallbacks = cached_search(
        normalized_categories, rounded_lat, rounded_lon, max_radius
    )
    return list(results), list(fallbacks)


def clear_catalog():
    """Clears all records from RESOURCE_CATALOG and resets the LRU cache."""
    RESOURCE_CATALOG.clear()
    cached_search.cache_clear()


def add_resource(category, name, lat, lon, fallback=None):
    """
    Inserts a new (name, lat, lon) resource in O(1) average time
    and clears the LRU cache to prevent stale search results.
    """
    validate_coordinates(lat, lon)

    if category not in RESOURCE_CATALOG:
        default_msg = (
            fallback
            if fallback is not None
            else f"No walkable {category} nearby. Contact: Local Helpline (211)"
        )
        RESOURCE_CATALOG[category] = {"resources": [], "fallback": default_msg}

    RESOURCE_CATALOG[category]["resources"].append((name, lat, lon))
    cached_search.cache_clear()