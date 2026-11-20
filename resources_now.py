"""
ResourcesNow - Location-Based Service (LBS)
Phase 3: Dictionary Catalog, Randomized Quicksort, and Bounded LRU Caching
"""

from functools import lru_cache
import random

# 1. Hash-Table Catalog: O(1) expected category lookup and self-contained records
RESOURCE_CATALOG = {
    "Food Bank": {
        "resources": [
            (1.2, "Downtown Pantry"),
            (0.4, "Community Kitchen"),
            (2.5, "Westside Food Hub"),
        ],
        "fallback": "211 Food Assistance Hotline",
    },
    "Housing": {
        "resources": [
            (3.1, "Hope Shelter"),
            (2.8, "City Transitional"),
        ],
        "fallback": "State Housing Authority (211)",
    },
    "Medical": {
        "resources": [
            (0.8, "Free Clinic A"),
            (0.3, "Urgent Care Center"),
        ],
        "fallback": "Statewide Nurse Advice Line",
    },
}


# 2. In-Place Randomized Quicksort
def _randomized_partition(arr, low, high):
    pivot_idx = random.randint(low, high)
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def _randomized_quicksort(arr, low, high):
    if low < high:
        q = _randomized_partition(arr, low, high)
        _randomized_quicksort(arr, low, q - 1)
        _randomized_quicksort(arr, q + 1, high)


def quicksort_resources(resource_tuples, max_radius=None):
    """Validates and sorts (distance, name) tuples in place."""
    for distance, _ in resource_tuples:
        if distance < 0:
            raise ValueError(
                f"GPS calculation error: negative distance ({distance} mi) detected."
            )
        if max_radius is not None and distance > max_radius:
            raise ValueError(
                f"Filter error: distance ({distance} mi) exceeds max_radius ({max_radius} mi)."
            )

    if len(resource_tuples) > 1:
        _randomized_quicksort(resource_tuples, 0, len(resource_tuples) - 1)
    return resource_tuples


# 3. Cached Search and Filter Workflow
@lru_cache(maxsize=64)
def _cached_search(categories_key, max_radius):
    walkable = []
    fallbacks = []

    for category in categories_key:
        category_data = RESOURCE_CATALOG.get(category)
        if category_data is None:
            continue

        matches = []
        for dist, name in category_data["resources"]:
            if dist < 0:
                raise ValueError(
                    f"GPS calculation error: negative distance ({dist} mi) for {name}."
                )
            if dist <= max_radius:
                matches.append((dist, name))

        if matches:
            walkable.extend(matches)
        else:
            fallbacks.append(
                f"No walkable {category} nearby. Contact: {category_data['fallback']}"
            )

    if walkable:
        quicksort_resources(walkable, max_radius=max_radius)

    return tuple(walkable), tuple(fallbacks)


def find_walkable_resources(user_categories, max_radius=1.5):
    """Normalizes query inputs and returns fresh copies from the bounded cache."""
    categories_key = tuple(sorted(set(user_categories)))
    results, fallbacks = _cached_search(categories_key, max_radius)
    return list(results), list(fallbacks)


def add_resource(category, distance, name, fallback=None):
    """Adds a facility to RESOURCE_CATALOG and clears stale cache entries."""
    if category not in RESOURCE_CATALOG:
        RESOURCE_CATALOG[category] = {
            "resources": [],
            "fallback": fallback or f"Contact 211 for {category} assistance",
        }
    RESOURCE_CATALOG[category]["resources"].append((distance, name))
    _cached_search.cache_clear()


if __name__ == "__main__":
    results, fallbacks = find_walkable_resources(["Food Bank", "Medical"], max_radius=1.5)
    print("Walkable Resources:", results)
    print("Fallbacks:", fallbacks)