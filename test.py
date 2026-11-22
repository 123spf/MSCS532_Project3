"""
ResourcesNow - Phase 3 Automated Test Suite
Tests fallback logic, Quicksort accuracy, 0.5/1.5-mile preset boundaries,
GPS validation, rounded-coordinate LRU caching, cache coherency, eviction,
and 5,000-resource high-volume sorting.
"""

from data_generator import generate_benchmark_records
from resources_now import (
    DEFAULT_USER_LAT,
    DEFAULT_USER_LON,
    RESOURCE_CATALOG,
    add_resource,
    cached_search,
    calculate_distance,
    find_walkable_resources,
    quicksort_resources,
)


def run_tests():
    base_lat = DEFAULT_USER_LAT
    base_lon = DEFAULT_USER_LON
    print("Running ResourcesNow Phase 3 Test Suite...\n")

    # Test 1: 211 Fallback Trigger
    RESOURCE_CATALOG.clear()
    cached_search.cache_clear()
    add_resource(
        "Housing",
        "Regional Shelter",
        base_lat + (4.0 / 69.0),
        base_lon,
        fallback="No walkable Housing nearby. Contact: State Housing Authority (211)",
    )
    results, fallbacks = find_walkable_resources(["Housing"], max_radius=1.5)
    assert results == []
    assert len(fallbacks) == 1
    print(f"Test 1  (211 Fallback)      | PASSED | fallbacks={fallbacks}")

    # Test 2: Empty Input Handling
    empty_result = quicksort_resources([])
    assert empty_result == []
    print(f"Test 2  (Empty List)        | PASSED | output={empty_result}")

    # Test 3: Randomized Quicksort and Alphabetical Tie-Breaking
    sample = [
        (1.2, "Downtown Pantry"),
        (0.4, "Community Kitchen"),
        (0.4, "Alpha Pantry"),
        (0.8, "Free Clinic A"),
    ]
    sorted_sample = quicksort_resources(sample)
    expected = [
        (0.4, "Alpha Pantry"),
        (0.4, "Community Kitchen"),
        (0.8, "Free Clinic A"),
        (1.2, "Downtown Pantry"),
    ]
    assert sorted_sample == expected
    print("Test 3  (Quicksort Order)   | PASSED | ascending distance + alphabetical tie-break")

    # Test 4: Exact Preset Boundary Checks (0.5 mi and 1.5 mi)
    RESOURCE_CATALOG.clear()
    cached_search.cache_clear()
    add_resource("Food Bank", "Half-Mile Pantry", base_lat + (0.5 / 69.0), base_lon)
    add_resource("Food Bank", "Boundary Pantry", base_lat + (1.5 / 69.0), base_lon)
    add_resource("Food Bank", "Westside Food Hub", base_lat + (2.0 / 69.0), base_lon)

    res_05, _ = find_walkable_resources(["Food Bank"], max_radius=0.5)
    res_15, _ = find_walkable_resources(["Food Bank"], max_radius=1.5)
    assert res_05 == [(0.5, "Half-Mile Pantry")]
    assert res_15 == [(0.5, "Half-Mile Pantry"), (1.5, "Boundary Pantry")]
    print("Test 4  (Preset Boundaries) | PASSED | 0.5 mi=1 match, 1.5 mi=2 matches, 2.0 mi excluded")

    # Test 5: GPS Validation (Negative Distance and Invalid Coordinates)
    negative_caught = False
    try:
        quicksort_resources([(-0.5, "Glitch Clinic")])
    except ValueError:
        negative_caught = True

    invalid_coord_caught = False
    try:
        calculate_distance(95.0, base_lon, base_lat, base_lon)
    except ValueError:
        invalid_coord_caught = True

    assert negative_caught is True
    assert invalid_coord_caught is True
    print("Test 5  (GPS Validation)    | PASSED | ValueError raised for -0.5 mi and lat=95.0")

    # Test 6: Unknown Category and Duplicate Category Deduplication
    dedup_res, dedup_fb = find_walkable_resources(
        ["Food Bank", "Food Bank", "Unknown Category"], max_radius=0.5
    )
    assert dedup_res == [(0.5, "Half-Mile Pantry")]
    assert dedup_fb == []
    print("Test 6  (Unknown/Dedup)     | PASSED | ignored unknown category and deduplicated query")

    # Test 7: Rounded-GPS LRU Cache Hit
    cached_search.cache_clear()
    find_walkable_resources(["Food Bank"], user_lat=40.0001, user_lon=-76.0001, max_radius=1.5)
    find_walkable_resources(["Food Bank"], user_lat=40.0004, user_lon=-76.0004, max_radius=1.5)
    info7 = cached_search.cache_info()
    assert info7.hits == 1
    assert info7.misses == 1
    assert info7.maxsize == 64
    assert info7.currsize == 1
    print(f"Test 7  (Rounded-GPS Cache) | PASSED | {info7}")

    # Test 8: Dynamic Insertion and Cache Coherency
    add_resource("Food Bank", "Corner Kitchen", base_lat + (0.2 / 69.0), base_lon)
    assert cached_search.cache_info().currsize == 0
    fresh_res, _ = find_walkable_resources(["Food Bank"], max_radius=0.5)
    assert fresh_res[0] == (0.2, "Corner Kitchen")
    print("Test 8  (Cache Coherency)   | PASSED | add_resource cleared stale cache and returned new resource")

    # Test 9: LRU Cache Eviction Stress Test (100 Unique Queries > maxsize=64)
    cached_search.cache_clear()
    for i in range(1, 101):
        radius = round(i * 0.1, 1)
        find_walkable_resources(["Food Bank"], max_radius=radius)

    mid_info = cached_search.cache_info()
    assert mid_info.hits == 0
    assert mid_info.misses == 100
    assert mid_info.currsize == 64

    # Check newest query (10.0) and oldest query (0.1)
    find_walkable_resources(["Food Bank"], max_radius=10.0)
    find_walkable_resources(["Food Bank"], max_radius=0.1)

    end_info = cached_search.cache_info()
    assert end_info.hits == 1
    assert end_info.misses == 101
    assert end_info.currsize == 64
    print(f"Test 9  (Cache Eviction)    | PASSED | {end_info}")

    # Test 10: High-Volume 5,000-Resource Clustered Sort Integrity
    large_records = generate_benchmark_records(5000, max_radius=1.5, distribution="clustered", seed=42)
    sorted_large = quicksort_resources(large_records)
    assert len(sorted_large) == 5000

    for i in range(len(sorted_large) - 1):
        assert sorted_large[i] <= sorted_large[i + 1]

    print("Test 10 (5,000-Resource Sort) | PASSED | 5,000 clustered GPS resources verified in order")
    print("\nAll 10 tests passed.")


if __name__ == "__main__":
    run_tests()