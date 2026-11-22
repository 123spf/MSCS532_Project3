"""
ResourcesNow - Synthetic Dataset Generator
Generates reproducible (name, lat, lon) resource facility records using Python's
standard library random module for demos, stress testing, and benchmarking.
"""

import math
import random

from resources_now import (
    DEFAULT_USER_LOCATION,
    RESOURCE_CATALOG,
    WALKABLE_PRESETS,
    cached_search,
    calculate_distance,
    clear_catalog,
    find_walkable_resources,
    validate_coordinates,
)

DEFAULT_CATEGORIES = ("Food Bank", "Housing", "Medical")


def _random_point_within_radius(center_lat, center_lon, radius_miles, rng):
    """
    Generates a random (lat, lon) coordinate guaranteed to stay inside radius_miles
    under Euclidean distance without requiring trigonometry.
    """
    max_axis_deg = ((radius_miles - 0.001) / 69.0) / math.sqrt(2)
    fac_lat = center_lat + rng.uniform(-max_axis_deg, max_axis_deg)
    fac_lon = center_lon + rng.uniform(-max_axis_deg, max_axis_deg)
    return fac_lat, fac_lon


def populate_random_catalog(
    num_resources,
    categories=DEFAULT_CATEGORIES,
    center_lat=DEFAULT_USER_LOCATION[0],
    center_lon=DEFAULT_USER_LOCATION[1],
    max_spread_miles=2.0,
    distribution="uniform",
    seed=42,
):
    """
    Populates RESOURCE_CATALOG with synthetic (name, lat, lon) tuples.
    Supports 'uniform' (spread-out) and 'clustered' (downtown core) layouts.
    """
    validate_coordinates(center_lat, center_lon)
    clear_catalog()
    rng = random.Random(seed)

    for category in categories:
        RESOURCE_CATALOG[category] = {
            "resources": [],
            "fallback": f"No walkable {category} nearby. Contact: Local Helpline (211)",
        }

    for i in range(num_resources):
        category = categories[i % len(categories)]
        name = f"{category} Site {i + 1}"

        # In clustered mode, place 80% of facilities within a 0.25-mile downtown block
        if distribution == "clustered" and rng.random() < 0.8:
            radius = min(0.25, max_spread_miles)
        else:
            radius = max_spread_miles

        fac_lat, fac_lon = _random_point_within_radius(center_lat, center_lon, radius, rng)
        RESOURCE_CATALOG[category]["resources"].append((name, fac_lat, fac_lon))

    cached_search.cache_clear()


def generate_benchmark_records(
    num_resources,
    center_lat=DEFAULT_USER_LOCATION[0],
    center_lon=DEFAULT_USER_LOCATION[1],
    max_radius=1.5,
    distribution="uniform",
    seed=42,
):
    """
    Generates a list of (distance, name) tuples calculated from synthetic GPS coordinates
    guaranteed to fall within max_radius, ready for cross-phase sorting benchmarks.
    """
    validate_coordinates(center_lat, center_lon)
    rng = random.Random(seed)
    records = []

    for i in range(num_resources):
        name = f"Facility {i + 1}"
        if distribution == "clustered" and rng.random() < 0.8:
            radius = min(0.25, max_radius)
        else:
            radius = max_radius

        fac_lat, fac_lon = _random_point_within_radius(center_lat, center_lon, radius, rng)
        dist = calculate_distance(center_lat, center_lon, fac_lat, fac_lon)
        records.append((dist, name))

    return records


if __name__ == "__main__":
    # Quick demo: generate 15 synthetic facilities and query both walkable presets
    populate_random_catalog(15, distribution="uniform", seed=42)

    for preset in WALKABLE_PRESETS:
        results, fallbacks = find_walkable_resources(
            ["Food Bank", "Medical", "Housing"], max_radius=preset
        )
        print(f"\nWalkable Resources ({preset} mi): {len(results)} found")
        for dist, name in results:
            print(f"  {dist:.4f} mi - {name}")
        print(f"Fallbacks: {fallbacks}")