"""
ResourcesNow - Phase 3 Test Suite
Verifies fallback logic, sorting accuracy, boundary/error handling,
dictionary lookups, LRU caching, and cache invalidation.
"""

from resources_now import (
    find_walkable_resources,
    quicksort_resources,
    add_resource,
    _cached_search,
)


def run_tests():
    _cached_search.cache_clear()

    # Test 1: 211 Fallback Trigger
    cat_input = ["Housing"]
    results, fallbacks = find_walkable_resources(cat_input, max_radius=1.5)
    assert results == [] and len(fallbacks) == 1
    print(f"Test 1 (211 Fallback)   | Passed -> fallbacks={fallbacks}")

    # Test 2: Empty Input Handling
    empty_result = quicksort_resources([], max_radius=1.5)
    assert empty_result == []
    print("Test 2 (Empty List)     | Passed -> []")

    # Test 3: Randomized Quicksort Correctness
    sample = [(1.2, "Downtown Pantry"), (0.4, "Community Kitchen"), (0.8, "Free Clinic A")]
    sorted_res = quicksort_resources(sample.copy(), max_radius=1.5)
    assert sorted_res[0][1] == "Community Kitchen" and sorted_res[-1][1] == "Downtown Pantry"
    print(f"Test 3 (Quicksort)      | Passed -> {sorted_res}")

    # Test 4: Exact Boundary Limit (1.5 miles)
    boundary_item = [(1.5, "Boundary Clinic")]
    assert quicksort_resources(boundary_item, max_radius=1.5) == [(1.5, "Boundary Clinic")]
    print("Test 4 (Boundary 1.5mi) | Passed")

    # Test 5: Error Handling (GPS Glitch)
    try:
        quicksort_resources([(-0.5, "Glitch Clinic")], max_radius=1.5)
        assert False, "Expected ValueError for negative distance"
    except ValueError as err:
        print(f"Test 5 (GPS Glitch)     | Passed -> Raised ValueError: {err}")

    # Test 6: Unknown Category Handling (O(1) dict .get())
    unknown_res, unknown_fb = find_walkable_resources(["Legal Aid"], max_radius=1.5)
    assert unknown_res == [] and unknown_fb == []
    print("Test 6 (Unknown Cat.)   | Passed -> ([], [])")

    # Test 7: LRU Cache Normalization, Hits, and Mutation Safety
    _cached_search.cache_clear()
    res_a, _ = find_walkable_resources(["Food Bank", "Medical"], max_radius=1.5)
    res_a.append((9.9, "Mutated Entry"))  # Attempt to alter returned list
    res_b, _ = find_walkable_resources(["Medical", "Food Bank"], max_radius=1.5)
    info = _cached_search.cache_info()
    assert info.misses == 1 and info.hits == 1
    assert (9.9, "Mutated Entry") not in res_b
    print(f"Test 7 (LRU Cache)      | Passed -> {info}")

    # Test 8: Dynamic Update & Cache Invalidation via add_resource
    add_resource("Housing", 0.5, "New Downtown Shelter")
    updated_res, updated_fb = find_walkable_resources(["Housing"], max_radius=1.5)
    assert updated_res == [(0.5, "New Downtown Shelter")] and updated_fb == []
    print(f"Test 8 (Dynamic Update) | Passed -> {updated_res}")


if __name__ == "__main__":
    run_tests()