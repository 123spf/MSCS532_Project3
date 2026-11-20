"""
ResourcesNow - Phase 3 Baseline Benchmark
Measures time and memory for Merge Sort vs. Bucket Sort + Heapsort
across uniform, clustered, and repeated-query workloads.
"""

import random
import time
import tracemalloc
from resources_now import bucket_sort_resources, find_walkable_resources


def merge_sort(arr, low, high):
    """Phase 1 baseline: recursively divides and sorts resource tuples."""
    if low >= high:
        return
    mid = (low + high) // 2
    merge_sort(arr, low, mid)
    merge_sort(arr, mid + 1, high)
    merge(arr, low, mid, high)


def merge(arr, low, mid, high):
    """Merges two sorted subarrays using O(n) auxiliary lists."""
    left = arr[low:mid + 1]
    right = arr[mid + 1:high + 1]
    i = j = 0
    k = low

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1

    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1

    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1


def run_merge_sort(data):
    merge_sort(data, 0, len(data) - 1)
    return data


def randomized_partition(arr, low, high):
    """Partitions subarray around a randomly chosen pivot (CLRS 7.1 & 7.3)."""
    pivot_idx = random.randint(low, high)
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def randomized_quicksort(arr, low, high):
    if low < high:
        q = randomized_partition(arr, low, high)
        randomized_quicksort(arr, low, q - 1)
        randomized_quicksort(arr, q + 1, high)


def run_quicksort(data):
    randomized_quicksort(data, 0, len(data) - 1)
    return data


def time_sort_ms(sort_fn, sample, runs=3):
    """Returns average runtime (ms) over multiple runs and the sorted output."""
    total_ms = 0.0
    result = None
    for _ in range(runs):
        data = sample.copy()
        t0 = time.perf_counter()
        result = sort_fn(data)
        total_ms += (time.perf_counter() - t0) * 1000
    return total_ms / runs, result


def measure_memory_kb(sort_fn, sample):
    """Returns (current_kb, peak_kb) allocated during sort_fn only."""
    data = sample.copy()
    tracemalloc.start()
    sort_fn(data)
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current_bytes / 1024, peak_bytes / 1024


def run_sort_scenario(label, generator, sizes, max_radius=1.5):
    print(f"\n--- {label} (max_radius = {max_radius} mi) ---")
    for n in sizes:
        sample = generator(n, max_radius)

        merge_ms, merge_out = time_sort_ms(run_merge_sort, sample)
        bucket_ms, bucket_out = time_sort_ms(
            lambda d: bucket_sort_resources(d, max_radius), sample
        )
        quick_ms, quick_out = time_sort_ms(run_quicksort, sample)
        assert merge_out == bucket_out == quick_out, "Sort outputs do not match!"

        _, merge_kb = measure_memory_kb(run_merge_sort, sample)
        _, bucket_kb = measure_memory_kb(
            lambda d: bucket_sort_resources(d, max_radius), sample
        )
        _, quick_kb = measure_memory_kb(run_quicksort, sample)

        print(
            f"n={n:<5} | Merge: {merge_ms:6.2f} ms ({merge_kb:5.1f} KB) "
            f"| Bucket+Heap: {bucket_ms:6.2f} ms ({bucket_kb:5.1f} KB) "
            f"| Quick: {quick_ms:6.2f} ms ({quick_kb:5.1f} KB)"
        )


def benchmark_repeated_queries(repeats=1000, max_radius=1.5):
    """Baselines repeated full-pipeline queries before adding caching."""
    print(f"\n--- Repeated Query Baseline ({repeats} identical calls) ---")
    t0 = time.perf_counter()
    for _ in range(repeats):
        find_walkable_resources(["Food Bank", "Medical"], max_radius=max_radius)
    total_ms = (time.perf_counter() - t0) * 1000

    tracemalloc.start()
    for _ in range(repeats):
        find_walkable_resources(["Food Bank", "Medical"], max_radius=max_radius)
    curr_b, peak_b = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(
        f"Total: {total_ms:.3f} ms | Retained: {curr_b / 1024:.2f} KB | "
        f"Peak: {peak_b / 1024:.2f} KB"
    )


if __name__ == "__main__":
    random.seed(42)
    sizes = (10, 250, 500, 1000, 5000, 10000)

    # 1. Spread-out neighborhoods (uniform distances)
    run_sort_scenario(
        "Spread-Out Uniform",
        lambda n, r: [(random.uniform(0.05, r), f"Facility {i}") for i in range(n)],
        sizes,
    )

    # 2. Dense downtown cluster (heavy bucket collisions & tied distances)
    run_sort_scenario(
        "Clustered Downtown",
        lambda n, r: [(round(random.uniform(0.40, 0.45), 2), f"Facility {i}") for i in range(n)],
        sizes,
    )

    # 3. Repeated full queries (no cache yet)
    benchmark_repeated_queries()