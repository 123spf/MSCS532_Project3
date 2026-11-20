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
        assert merge_out == bucket_out, "Sort outputs do not match!"

        _, merge_peak_kb = measure_memory_kb(run_merge_sort, sample)
        _, bucket_peak_kb = measure_memory_kb(
            lambda d: bucket_sort_resources(d, max_radius), sample
        )

        print(
            f"n={n:<5} | Merge: {merge_ms:7.3f} ms ({merge_peak_kb:7.1f} KB peak) "
            f"| Bucket+Heap: {bucket_ms:7.3f} ms ({bucket_peak_kb:7.1f} KB peak)"
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