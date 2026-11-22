"""
ResourcesNow - Synthetic Dataset Generator
Creates reproducible (name, lat, lon) resource records using Python's
built-in random module for demos, stress testing, and benchmarking.
"""

import random

from resources_now import (
    DEFAULT_USER_LAT,
    DEFAULT_USER_LON,
    RESOURCE_CATALOG,
    WALKABLE_PRESETS,
    cached_search,
    calculate_distance,
    find_walkable_resources,
)

DEFAULT_CATEGORIES = ("Food Bank", "Housing", "Medical")


def populate_random_catalog(num_resources, distribution="uniform", seed=42):
    """
    Fills RESOURCE_CATALOG with synthetic (name, lat, lon) resource tuples.
    Supports 'uniform' (spread out) and 'clustered' (downtown core) layouts.
    """
    random.seed(seed)
    RESOURCE_CATALOG.clear()
    cached_search.cache_clear()

    # Set up each category with an empty resource list and 211 fallback
    for category in DEFAULT_CATEGORIES:
        RESOURCE_CATALOG[category] = {
            "resources": [],
            "fallback": f"No walkable {category} nearby. Contact: Local Helpline (211)",
        }

    for i in range(num_resources):
        category = DEFAULT_CATEGORIES[i % len(DEFAULT_CATEGORIES)]
        name = f"{category} Resource {i + 1}"

        # In clustered mode, place 80% of resources inside a 0.25-mile downtown area
        if distribution == "clustered" and random.random() < 0.8:
            spread_miles = 0.25
        else:
            spread_miles = 2.0

        spread_deg = spread_miles / 69.0
        resource_lat = DEFAULT_USER_LAT + random.uniform(-spread_deg, spread_deg)
        resource_lon = DEFAULT_USER_LON + random.uniform(-spread_deg, spread_deg)

        RESOURCE_CATALOG[category]["resources"].append((name, resource_lat, resource_lon))


def generate_benchmark_records(num_resources, max_radius=1.5, distribution="uniform", seed=42):
    """
    Generates (distance, name) resource tuples calculated from random GPS coordinates
    that all fall within max_radius miles for sorting benchmarks.
    """
    random.seed(seed)
    records = []
    count = 1

    while len(records) < num_resources:
        if distribution == "clustered" and random.random() < 0.8:
            spread_miles = 0.25
        else:
            spread_miles = max_radius

        spread_deg = spread_miles / 69.0
        resource_lat = DEFAULT_USER_LAT + random.uniform(-spread_deg, spread_deg)
        resource_lon = DEFAULT_USER_LON + random.uniform(-spread_deg, spread_deg)

        dist = calculate_distance(
            DEFAULT_USER_LAT, DEFAULT_USER_LON, resource_lat, resource_lon
        )

        # Keep only coordinates that stay inside the exact walking radius
        if dist <= max_radius:
            name = f"Resource {count}"
            records.append((dist, name))
            count = count + 1

    return records


if __name__ == "__main__":
    populate_random_catalog(15, distribution="uniform", seed=42)

    for preset in WALKABLE_PRESETS:
        results, fallbacks = find_walkable_resources(
            ["Food Bank", "Medical", "Housing"], max_radius=preset
        )
        print(f"\nWalkable Resources ({preset} mi): {len(results)} found")
        for dist, name in results:
            print(f"  {dist:.4f} mi - {name}")
        print(f"Fallbacks: {fallbacks}")