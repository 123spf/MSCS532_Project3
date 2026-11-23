# ResourcesNow: Phase 3

**Author:** Stephanie Peguero  
**Course:** MSCS-532-B01 (Algorithms and Data Structures)

## Overview

ResourcesNow is a location-based community resource locator that finds nearby walkable services (food banks, housing shelters, and medical clinics). Phase 3 optimizes the core engine for memory-constrained mobile devices using only Python's standard library (Python 3.8+, no external packages).

## Key Optimizations

* **Dictionary Catalog & Tuples:** Replaces parallel lists with `RESOURCE_CATALOG` for $O(1)$ average-case lookups and stores each resource as a compact `(name, resource_lat, resource_lon)` tuple.
* **Live Euclidean GPS Distance:** Calculates straight-line distance in miles inside `calculate_distance()` with coordinate validation.
* **In-Place Randomized Quicksort:** Sorts `(distance, name)` matches in expected $O(n \log n)$ time and $O(\log n)$ call-stack space, eliminating Bucket Sort's linear memory overhead.
* **Bounded Rounded-GPS LRU Cache:** Uses `@lru_cache(maxsize=64)` with three-decimal-place GPS rounding (about 0.07 miles) to accelerate repeat nearby queries; `add_resource()` clears the cache to prevent stale results.

## Files

* `resources_now.py` - Core engine (catalog, GPS distance math, LRU cache, Randomized Quicksort).
* `data_generator.py` - Reproducible synthetic GPS dataset generator (`random.seed(42)`) and walkable preset demo.
* `test.py` - 10-case automated test suite (boundaries, GPS validation, cache eviction, and 5,000-resource sorting).
* `benchmark.py` - Cross-phase runtime (ms), peak memory (KB), and cache speedup benchmarks.

## How to Run

```bash
python3 data_generator.py   # Run 0.5 mi and 1.5 mi preset demo
python3 test.py             # Run 10-case automated test suite
python3 benchmark.py        # Run Phase 1-3 speed, memory, and cache benchmarks
```

## Key Results

* **Validation:** All 10 automated tests in `test.py` pass.
* **Peak Sorting Memory ($n = 10,000$):** Phase 3 Quicksort peaked at `2.1 KB` on both uniform and clustered data, reducing peak memory by **99.8%** compared to Phase 2 Bucket+Heap (`886.5 KB` uniform / `847.2 KB` clustered) and **97.3%** compared to Phase 1 Merge Sort (`78.3 KB`).
* **Sorting Speed ($n = 10,000$):** Quicksort finished in `22.20 ms` (uniform) and `67.53 ms` (clustered), keeping every cold sort under the 100 ms interactive delay threshold.
* **Cache Speedup ($n = 1,000$):** Rounded-GPS caching cut query time from `1.5433 ms` (miss) to `0.0083 ms` (hit), achieving a **186.1x speedup**.