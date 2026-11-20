"""
ResourcesNow - Phase 3 Simple Test Suite
"""
import random
from resources_now import (
    find_walkable_resources,
    quicksort_resources,
    cached_search,
    add_resource,
)


def run_tests():
    # Test 1: 211 Fallback Trigger
    results, fallbacks = find_walkable_resources(["Housing"], max_radius=1.5)
    assert results == []
    assert len(fallbacks) == 1
    print("Test 1 (211 Fallback)   | Passed")

    # Test 2: Empty List Handling
    assert quicksort_resources([]) == []
    print("Test 2 (Empty List)     | Passed")

    # Test 3: Sorting Accuracy
    sample = [(1.2, "Downtown Pantry"), (0.4, "Community Kitchen"), (0.8, "Free Clinic A")]
    sorted_items = quicksort_resources(sample)
    assert sorted_items[0] == (0.4, "Community Kitchen")
    assert sorted_items[-1] == (1.2, "Downtown Pantry")
    print("Test 3 (Quicksort)      | Passed")

    # Test 4: Exact Distance Boundary (1.2 miles)
    boundary_res, _ = find_walkable_resources(["Food Bank"], max_radius=1.2)
    assert (1.2, "Downtown Pantry") in boundary_res
    assert (2.5, "Westside Food Hub") not in boundary_res
    print("Test 4 (Boundary Check) | Passed")

    # Test 5: Negative Distance Error
    try:
        quicksort_resources([(-0.5, "Glitch Clinic")])
        assert False, "Expected ValueError"
    except ValueError:
        print("Test 5 (GPS Glitch)     | Passed")

    # Test 6: Unknown Category
    unknown_res, unknown_fb = find_walkable_resources(["Legal Aid"])
    assert unknown_res == []
    assert unknown_fb == []
    print("Test 6 (Unknown Cat.)   | Passed")

    # Test 7: LRU Cache Hit on Reordered Query
    cached_search.cache_clear()
    find_walkable_resources(["Food Bank", "Medical"], max_radius=1.5)
    find_walkable_resources(["Medical", "Food Bank"], max_radius=1.5)
    info = cached_search.cache_info()
    assert info.misses == 1
    assert info.hits == 1
    print(f"Test 7 (LRU Cache)      | Passed -> {info}")

    # Test 8: Adding a New Resource Clears the Cache
    add_resource("Housing", 0.5, "New Downtown Shelter")
    new_res, new_fb = find_walkable_resources(["Housing"], max_radius=1.5)
    assert new_res == [(0.5, "New Downtown Shelter")]
    assert new_fb == []
    print("Test 8 (Add Resource)   | Passed")

    # Test 9: Stress Test - Cache Eviction Past maxsize=64
    cached_search.cache_clear()
    for i in range(1, 101):
        radius = round(i * 0.1, 1)
        find_walkable_resources(["Food Bank"], max_radius=radius)

    info = cached_search.cache_info()
    assert info.currsize == 64
    assert info.misses == 100

    # Most recent query (10.0) stays cached; oldest query (0.1) was evicted
    find_walkable_resources(["Food Bank"], max_radius=10.0)
    assert cached_search.cache_info().hits == 1
    find_walkable_resources(["Food Bank"], max_radius=0.1)
    assert cached_search.cache_info().misses == 101
    print(f"Test 9 (Cache Stress)   | Passed -> {cached_search.cache_info()}")

    # Test 10: Stress Test - High-Volume Quicksort (5,000 Resources)
    random.seed(42)
    large_list = []
    for i in range(5000):
        dist = round(random.uniform(0.0, 1.5), 3)
        large_list.append((dist, f"Site_{i}"))

    sorted_large = quicksort_resources(large_list)
    for i in range(len(sorted_large) - 1):
        assert sorted_large[i][0] <= sorted_large[i + 1][0]
    print("Test 10 (5,000 Sort)    | Passed")

if __name__ == "__main__":
    run_tests()