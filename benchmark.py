"""
ResourcesNow - Phase 3 Performance and Memory Benchmark
Compares Phase 1 (Merge Sort), Phase 2 (Bucket+Heap), and Phase 3 (Randomized Quicksort)
on execution time (ms) and peak traced memory (KB) across uniform and clustered GPS data,
and measures rounded-GPS LRU cache speedup at n = 1,000 resources.
"""

import random
import time
import tracemalloc

from data_generator import generate_benchmark_records, populate_random_catalog
from resources_now import cached_search, find_walkable_resources, quicksort_resources


# --- Phase 1 Baseline: Merge Sort ---
def merge(arr, left, mid, right):
    left_half = arr[left : mid + 1]
    right_half = arr[mid + 1 : right + 1]
    i = 0
    j = 0
    k = left

    while i < len(left_half) and j < len(right_half):
        if left_half[i] <= right_half[j]:
            arr[k] = left_half[i]
            i = i + 1
        else:
            arr[k] = right_half[j]
            j = j + 1
        k = k + 1

    while i < len(left_half):
        arr[k] = left_half[i]
        i = i + 1
        k = k + 1

    while j < len(right_half):
        arr[k] = right_half[j]
        j = j + 1
        k = k + 1


def merge_sort_recursive(arr, left, right):
    if left < right:
        mid = (left + right) // 2
        merge_sort_recursive(arr, left, mid)
        merge_sort_recursive(arr, mid + 1, right)
        merge(arr, left, mid, right)


def merge_sort_resources(resource_tuples):
    if len(resource_tuples) > 1:
        merge_sort_recursive(resource_tuples, 0, len(resource_tuples) - 1)
    return resource_tuples


# --- Phase 2 Baseline: Bucket Sort + Heapsort ---
def max_heapify(arr, heap_size, root):
    largest = root
    left = 2 * root + 1
    right = 2 * root + 2

    if left < heap_size and arr[left] > arr[largest]:
        largest = left
    if right < heap_size and arr[right] > arr[largest]:
        largest = right

    if largest != root:
        arr[root], arr[largest] = arr[largest], arr[root]
        max_heapify(arr, heap_size, largest)


def heapsort_resources(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        max_heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        max_heapify(arr, i, 0)
    return arr


def bucket_sort_resources(resource_tuples, max_radius):
    n = len(resource_tuples)
    if n <= 1:
        return list(resource_tuples)

    buckets = []
    for _ in range(n):
        buckets.append([])

    for item in resource_tuples:
        normalized = item[0] / (max_radius + 0.01)
        index = int(n * normalized)
        buckets[index].append(item)

    result = []
    for bucket in buckets:
        if len(bucket) > 0:
            sorted_bucket = heapsort_resources(bucket)
            result.extend(sorted_bucket)

    return result


# --- Sorting Benchmark Runner ---
def run_sorting_benchmarks():
    sizes = [10, 250, 500, 1000, 5000, 10000]
    max_radius = 1.5
    distributions = [
        ("Spread-Out Uniform GPS Data", "uniform"),
        ("Clustered Downtown GPS Data", "clustered"),
    ]

    header = (
        f"{'Size (n)':<10} | {'Phase 1: Merge Sort':<22} | "
        f"{'Phase 2: Bucket+Heap':<22} | {'Phase 3: Quicksort':<22}"
    )
    divider = "-" * len(header)

    for label, dist_mode in distributions:
        print(f"\n=== {label} (max_radius = {max_radius} mi) ===")
        print(header)
        print(divider)

        for n in sizes:
            sample = generate_benchmark_records(
                n, max_radius=max_radius, distribution=dist_mode, seed=42
            )

            # 1. Phase 1: Merge Sort (Pass A: Time, Pass B: Memory)
            merge_time_data = sample.copy()
            start = time.perf_counter()
            merge_out = merge_sort_resources(merge_time_data)
            merge_ms = (time.perf_counter() - start) * 1000

            merge_mem_data = sample.copy()
            tracemalloc.start()
            merge_sort_resources(merge_mem_data)
            _, merge_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            merge_kb = merge_peak / 1024

            # 2. Phase 2: Bucket Sort + Heapsort (Pass A: Time, Pass B: Memory)
            bucket_time_data = sample.copy()
            start = time.perf_counter()
            bucket_out = bucket_sort_resources(bucket_time_data, max_radius)
            bucket_ms = (time.perf_counter() - start) * 1000

            bucket_mem_data = sample.copy()
            tracemalloc.start()
            bucket_sort_resources(bucket_mem_data, max_radius)
            _, bucket_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            bucket_kb = bucket_peak / 1024

            # 3. Phase 3: Randomized Quicksort (Pass A: Time, Pass B: Memory)
            quick_time_data = sample.copy()
            random.seed(42)
            start = time.perf_counter()
            quick_out = quicksort_resources(quick_time_data)
            quick_ms = (time.perf_counter() - start) * 1000

            quick_mem_data = sample.copy()
            random.seed(42)
            tracemalloc.start()
            quicksort_resources(quick_mem_data)
            _, quick_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            quick_kb = quick_peak / 1024

            # Confirm all three algorithms produced the exact same sorted list
            assert merge_out == bucket_out == quick_out

            p1 = f"{merge_ms:6.2f} ms ({merge_kb:5.1f} KB)"
            p2 = f"{bucket_ms:6.2f} ms ({bucket_kb:5.1f} KB)"
            p3 = f"{quick_ms:6.2f} ms ({quick_kb:5.1f} KB)"
            print(f"{n:<10} | {p1:<22} | {p2:<22} | {p3:<22}")

# --- Rounded-GPS LRU Cache Benchmark ---
def run_cache_benchmark():
    num_resources = 1000
    max_radius = 1.5

    populate_random_catalog(num_resources, distribution="uniform", seed=42)
    cached_search.cache_clear()

    # Cold query (cache miss) from first GPS reading
    start = time.perf_counter()
    find_walkable_resources(
        ["Food Bank", "Medical", "Housing"],
        user_lat=40.0001,
        user_lon=-76.0001,
        max_radius=max_radius,
    )
    cold_ms = (time.perf_counter() - start) * 1000

    # Warm query (cache hit) after a tiny GPS shift that rounds to the same grid cell
    start = time.perf_counter()
    find_walkable_resources(
        ["Food Bank", "Medical", "Housing"],
        user_lat=40.0004,
        user_lon=-76.0004,
        max_radius=max_radius,
    )
    warm_ms = (time.perf_counter() - start) * 1000

    speedup = cold_ms / warm_ms
    print(f"\n=== Rounded-GPS LRU Cache Benchmark (n = {num_resources}, max_radius = {max_radius} mi) ===")
    print(f"Cold Query (Cache Miss) : {cold_ms:.4f} ms")
    print(f"Warm Query (Cache Hit)  : {warm_ms:.4f} ms")
    print(f"Speedup Factor          : {speedup:.1f}x faster")
    print(f"Cache Status            : {cached_search.cache_info()}")


if __name__ == "__main__":
    run_sorting_benchmarks()
    run_cache_benchmark()