# Assignment 2 – Divide-and-Conquer Algorithms

Course: MSCS 532 – Algorithms and Data Structures  
University: University of the Cumberlands  
Author: Peter Nwochie Tiewah  
Repository: mscs-532-dsa

## Overview

This assignment explores divide-and-conquer algorithms through the implementation and performance analysis of Merge Sort and Quick Sort using Python.

Both algorithms are evaluated based on time complexity, memory usage, and practical efficiency across different datasets.

## Algorithms

| Algorithm | Average Time | Worst Time | Extra Space |
|---|---|---|---|
| Merge Sort | O(n log n) | O(n log n) | O(n) |
| Quick Sort | O(n log n) | O(n²) | O(log n) average |

Quick Sort uses first-element pivot selection with an iterative stack, while Merge Sort uses recursive splitting and merging.

## Benchmarking

Both algorithms are tested using:

- Dataset sizes: 500, 1,000, and 2,000 elements.
- Input types: random, sorted, and reverse-sorted.
- Five execution trials per test.
- Execution time measured with `time.perf_counter()`.
- Peak Python memory allocations measured with `tracemalloc`.

Results are saved in `benchmarks.csv`, with visual comparisons in `performance_graphs.png`.

## Run

```bash
python algorithms_benchmark.py
```

Requires Python 3.9 or later. No external dependencies.

## Project Files

- `algorithms_benchmark.py` – Algorithm implementations and benchmarks.
- `benchmarks.csv` – Performance results.
- `performance_graphs.png` – Performance visualizations.
- `Assignment_2_Divide_and_Conquer.docx` – Written analysis.

## Conclusion

Merge Sort provides predictable performance across different inputs, while Quick Sort performs efficiently on random datasets but can slow significantly on sorted or reverse-sorted data with first-element pivot selection.

The results highlight the importance of considering input characteristics, execution time, and memory requirements when selecting algorithms.