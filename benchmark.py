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