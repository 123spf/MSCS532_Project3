"""
ResourcesNow - Location-Based Service (LBS) Proof of Concept
Phase 2: Data Structures, Sorting Algorithms, and Error Handling
"""

from itertools import chain

# 1. Structure of Arrays (SoA): Parallel lists sorted alphabetically by category
categories = ["Food Bank", "Housing", "Medical"]

resource_names = [
    ["Downtown Pantry", "Community Kitchen", "Westside Food Hub"],
    ["Hope Shelter", "City Transitional"],
    ["Free Clinic A", "Urgent Care Center"]
]

resource_distances = [
    [1.2, 0.4, 2.5],
    [3.1, 2.8],
    [0.8, 0.3]
]

statewide_fallbacks = [
    "211 Food Assistance Hotline",
    "State Housing Authority (211)",
    "Statewide Nurse Advice Line"
]


# 2. Binary Search: Worst-case O(log n) category lookup
def binary_search_category(category_list, target):
    """Locates the index of a target category in a sorted list."""
    low, high = 0, len(category_list) - 1
    while low <= high:
        mid = (low + high) // 2
        if category_list[mid] == target:
            return mid
        elif category_list[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


# 3. Phase 3 Upgrade: Bounded Bucket Sort + Iterative Heapsort + Insertion Sort Cutoff
def insertion_sort_resources(resource_tuples):
    """Sorts small lists of (distance, name) tuples in place."""
    for i in range(1, len(resource_tuples)):
        key = resource_tuples[i]
        j = i - 1
        while j >= 0 and resource_tuples[j] > key:
            resource_tuples[j + 1] = resource_tuples[j]
            j -= 1
        resource_tuples[j + 1] = key
    return resource_tuples


def max_heapify(resource_tuples, n, i):
    """Iteratively maintains the max-heap property for (distance, name) tuples."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n and resource_tuples[left] > resource_tuples[largest]:
            largest = left
        if right < n and resource_tuples[right] > resource_tuples[largest]:
            largest = right

        if largest == i:
            break

        resource_tuples[i], resource_tuples[largest] = (
            resource_tuples[largest],
            resource_tuples[i],
        )
        i = largest


def heapsort_resources(resource_tuples):
    """Sorts resource tuples in place using O(1) auxiliary memory."""
    n = len(resource_tuples)
    for i in range(n // 2 - 1, -1, -1):
        max_heapify(resource_tuples, n, i)

    for i in range(n - 1, 0, -1):
        resource_tuples[i], resource_tuples[0] = resource_tuples[0], resource_tuples[i]
        max_heapify(resource_tuples, i, 0)
    return resource_tuples


def bucket_sort_resources(resource_tuples, max_radius, small_cutoff=16):
    """Groups resources into bounded spatial buckets and writes sorted results in place."""
    n = len(resource_tuples)
    if n == 0:
        return resource_tuples

    for distance, _ in resource_tuples:
        if distance < 0:
            raise ValueError(f"GPS calculation error: negative distance ({distance} mi) detected.")
        if distance > max_radius:
            raise ValueError(f"Filter error: distance ({distance} mi) exceeds max_radius ({max_radius} mi).")

    if n <= small_cutoff:
        return insertion_sort_resources(resource_tuples)

    num_buckets = max(1, int(n ** 0.5))
    buckets = [[] for _ in range(num_buckets)]

    for item in resource_tuples:
        normalized = item[0] / (max_radius + 0.01)
        index = int(num_buckets * normalized)
        buckets[index].append(item)

    pos = 0
    for bucket in buckets:
        if not bucket:
            continue
        if len(bucket) <= small_cutoff:
            insertion_sort_resources(bucket)
        else:
            heapsort_resources(bucket)
        for item in bucket:
            resource_tuples[pos] = item
            pos += 1

    return resource_tuples


# 4. Main Search and Filter Workflow
def find_walkable_resources(user_categories, max_radius=1.5):
    """Retrieves, filters, and sorts nearby resources within a walkable radius."""
    walkable_groups = []
    fallback_messages = []

    for category in user_categories:
        category_index = binary_search_category(categories, category)
        if category_index != -1:
            category_matches = []
            for dist, name in zip(resource_distances[category_index], resource_names[category_index]):
                if dist < 0:
                    raise ValueError(f"GPS calculation error: negative distance ({dist} mi) for {name}.")
                if dist <= max_radius:
                    category_matches.append((dist, name))

            if category_matches:
                walkable_groups.append(category_matches)
            else:
                fallback_messages.append(
                    f"No walkable {category} nearby. Contact: {statewide_fallbacks[category_index]}"
                )

    combined_walkable = list(chain(*walkable_groups))
    if combined_walkable:
        combined_walkable = bucket_sort_resources(combined_walkable, max_radius)

    return combined_walkable, fallback_messages


if __name__ == "__main__":
    results, fallbacks = find_walkable_resources(["Food Bank", "Medical"], max_radius=1.5)
    print("Walkable Resources:", results)
    print("Fallbacks:", fallbacks)