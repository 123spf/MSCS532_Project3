"""
ResourcesNow - Phase 3
Dictionary Catalog, Randomized Quicksort, and Bounded LRU Cache
"""

from functools import lru_cache
import random

# 1. Data Catalog (Dictionary)
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
def partition(items, low, high):
    # 1. Pick a random pivot and move it to the end
    pivot_index = random.randint(low, high)
    items[pivot_index], items[high] = items[high], items[pivot_index]
    pivot = items[high]

    # 2. Move items <= pivot to the left side
    smaller_end = low - 1
    for current in range(low, high):
        if items[current] <= pivot:
            smaller_end += 1
            items[smaller_end], items[current] = items[current], items[smaller_end]

    # 3. Place the pivot right after the smaller items
    pivot_pos = smaller_end + 1
    items[pivot_pos], items[high] = items[high], items[pivot_pos]
    return pivot_pos


def quicksort(items, low, high):
    if low < high:
        pivot_pos = partition(items, low, high)
        quicksort(items, low, pivot_pos - 1)
        quicksort(items, pivot_pos + 1, high)


def quicksort_resources(items):
    for distance, name in items:
        if distance < 0:
            raise ValueError(f"Negative distance ({distance} mi) for {name}")
    if len(items) > 1:
        quicksort(items, 0, len(items) - 1)
    return items


# 3. Cached Search and Dynamic Updates
@lru_cache(maxsize=64)
def cached_search(categories_key, max_radius):
    walkable = []
    fallbacks = []

    for category in categories_key:
        if category not in RESOURCE_CATALOG:
            continue

        data = RESOURCE_CATALOG[category]
        matches = []
        for distance, name in data["resources"]:
            if distance < 0:
                raise ValueError(f"Negative distance ({distance} mi) for {name}")
            if distance <= max_radius:
                matches.append((distance, name))

        if matches:
            walkable.extend(matches)
        else:
            fallbacks.append(f"No walkable {category} nearby. Contact: {data['fallback']}")

    if walkable:
        quicksort_resources(walkable)

    return tuple(walkable), tuple(fallbacks)


def find_walkable_resources(user_categories, max_radius=1.5):
    unique_categories = sorted(set(user_categories))
    categories_key = tuple(unique_categories)

    results, fallbacks = cached_search(categories_key, max_radius)
    return list(results), list(fallbacks)


def add_resource(category, distance, name, fallback="Contact 211 for assistance"):
    if category not in RESOURCE_CATALOG:
        RESOURCE_CATALOG[category] = {"resources": [], "fallback": fallback}
    RESOURCE_CATALOG[category]["resources"].append((distance, name))
    cached_search.cache_clear()


if __name__ == "__main__":
    results, fallbacks = find_walkable_resources(["Food Bank", "Medical"], max_radius=1.5)
    print("Walkable Resources:", results)
    print("Fallbacks:", fallbacks)