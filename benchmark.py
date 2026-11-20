"""
ResourcesNow - Phase 3 Benchmark
Compares Phase 1 (Merge Sort), Phase 2 (Bucket+Heap), Phase 3 (Quicksort),
and the Phase 3 LRU Cache speedup.
"""

import random
import time
import tracemalloc
from resources_now import (
    quicksort_resources,
    find_walkable_resources,
    cached_search,
    add_resource,
)


# Phase 1: Merge Sort
def merge_sort(items):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    return merge(left, right)


def merge(left, right):
    sorted_list = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list


# Phase 2: Bucket Sort + Heapsort
def max_heapify(items, size, root):
    largest = root
    left = 2 * root + 1
    right = 2 * root + 2

    if left < size and items[left] > items[largest]:
        largest = left
    if right < size and items[right] > items[largest]:
        largest = right

    if largest != root:
        items[root], items[largest] = items[largest], items[root]
        max_heapify(items, size, largest)


def heapsort(items):
    n = len(items)
    for i in range(n // 2 - 1, -1, -1):
        max_heapify(items, n, i)
    for i in range(n - 1, 0, -1):
        items[0], items[i] = items[i], items[0]
        max_heapify(items, i, 0)
    return items


def bucket_heap_sort(items, max_radius=1.5):
    n = len(items)
    if n == 0:
        return items

    buckets = [[] for _ in range(n)]
    for item in items:
        distance = item[0]
        index = int(n * (distance / (max_radius + 0.01)))
        buckets[index].append(item)

    result = []
    for bucket in buckets:
        if bucket:
            heapsort(bucket)
            result.extend(bucket)
    return result


# Data Generators
def make_uniform_data(size, max_radius=1.5):
    data = []
    for i in range(size):
        dist = round(random.uniform(0.0, max_radius), 3)
        data.append((dist, f"Site_{i}"))
    return data


def make_clustered_data(size):
    data = []
    for i in range(size):
        dist = round(random.uniform(0.0, 0.2), 3)
        data.append((dist, f"Downtown_{i}"))
    return data


# Measurement Helpers
def measure_sort(sort_func, sample):
    # Measure speed in milliseconds
    start = time.perf_counter()
    sort_func(sample.copy())
    time_ms = (time.perf_counter() - start) * 1000

    # Measure peak memory in KB
    data_copy = sample.copy()
    tracemalloc.start()
    sort_func(data_copy)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_kb = peak_bytes / 1024

    return time_ms, peak_kb


def benchmark_sorts(label, data_maker, sizes):
    print(f"\n--- {label} ---")
    for n in sizes:
        sample = data_maker(n)
        merge_ms, merge_kb = measure_sort(merge_sort, sample)
        bucket_ms, bucket_kb = measure_sort(bucket_heap_sort, sample)
        quick_ms, quick_kb = measure_sort(quicksort_resources, sample)

        print(
            f"n={n:<5} | Merge: {merge_ms:6.2f} ms ({merge_kb:5.1f} KB) "
            f"| Bucket+Heap: {bucket_ms:6.2f} ms ({bucket_kb:5.1f} KB) "
            f"| Quick: {quick_ms:6.2f} ms ({quick_kb:5.1f} KB)"
        )


def benchmark_cache():
    print("\n--- LRU Cache Speedup (1,000 Resources) ---")
    for i in range(1000):
        dist = round(random.uniform(0.0, 1.5), 3)
        add_resource("TestCategory", dist, f"Center_{i}")

    cached_search.cache_clear()

    # First search: Cache Miss
    start = time.perf_counter()
    find_walkable_resources(["TestCategory"], max_radius=1.5)
    miss_ms = (time.perf_counter() - start) * 1000

    # Second search: Cache Hit
    start = time.perf_counter()
    find_walkable_resources(["TestCategory"], max_radius=1.5)
    hit_ms = (time.perf_counter() - start) * 1000

    print(f"Cache Miss: {miss_ms:.4f} ms")
    print(f"Cache Hit:  {hit_ms:.4f} ms")
    print(f"Cache Info: {cached_search.cache_info()}")


if __name__ == "__main__":
    random.seed(42)
    sizes = [10, 250, 500, 1000, 5000, 10000]
    benchmark_sorts("Spread-Out Uniform", make_uniform_data, sizes)
    benchmark_sorts("Clustered Downtown", make_clustered_data, sizes)
    benchmark_cache()