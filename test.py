"""
ResourcesNow - Test Suite
Verifies fallback logic, empty inputs, sorting accuracy, boundary limits, and error handling.
"""

from resources_now import find_walkable_resources, heapsort_resources, bucket_sort_resources


def run_tests():
    # Test 1: 211 Fallback Trigger
    cat_input = ["Housing"]
    results, fallbacks = find_walkable_resources(cat_input, max_radius=1.5)
    assert results == [] and len(fallbacks) == 1
    print(f"Test 1 (211 Fallback) | Input: {cat_input}, radius=1.5")
    print(f"  Output: results={results}, fallbacks={fallbacks}")

    # Test 2: Empty Input Handling
    empty_input = []
    empty_result = bucket_sort_resources(empty_input, max_radius=1.5)
    assert empty_result == []
    print(f"Test 2 (Empty List)   | Input: {empty_input}, radius=1.5")
    print(f"  Output: {empty_result}")

    # Test 3: Heapsort Correctness
    sample_resources = [(1.2, "Downtown Pantry"), (0.4, "Community Kitchen"), (0.8, "Free Clinic A")]
    sorted_heap = heapsort_resources(sample_resources.copy())
    assert sorted_heap[0][1] == "Community Kitchen" and sorted_heap[-1][1] == "Downtown Pantry"
    print(f"Test 3 (Heapsort)     | Input: {sample_resources}")
    print(f"  Output: {sorted_heap}")

    # Test 4: Exact Boundary Limit (1.5 miles)
    boundary_item = [(1.5, "Boundary Clinic")]
    sorted_boundary = bucket_sort_resources(boundary_item, max_radius=1.5)
    assert sorted_boundary == [(1.5, "Boundary Clinic")]
    print(f"Test 4 (Boundary)     | Input: {boundary_item}, radius=1.5")
    print(f"  Output: {sorted_boundary}")

    # Test 5: Error Handling (GPS Glitch)
    glitch_input = [(-0.5, "Glitch Clinic")]
    print(f"Test 5 (GPS Glitch)   | Input: {glitch_input}, radius=1.5")
    try:
        bucket_sort_resources(glitch_input, max_radius=1.5)
        assert False
    except ValueError as err:
        print(f"  Raised ValueError: {err}")


if __name__ == "__main__":
    run_tests()