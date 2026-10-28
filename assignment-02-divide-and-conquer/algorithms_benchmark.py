import csv
import random
import statistics
import time
import tracemalloc
import platform
from pathlib import Path

"""
University of the Cumberlands
MSCS 532 - Algorithms and Data Structures

Assignment 2: Analyzing and Implementing Divide-and-Conquer Algorithms

Student Name: Peter Nwochie Tiewah
Student ID: 005064393
Date: October 28, 2026

Description:
    This program implements Merge Sort and Quick Sort using
    the divide-and-conquer approach.

    It compares execution time and peak traced Python memory
    across random, sorted, and reverse-sorted datasets.

Algorithms:
    1. Merge Sort
    2. Quick Sort (First-Element Pivot)

Run:
    python algorithms_benchmark.py

Output:
    benchmarks.csv

Dependencies:
    Python Standard Library only.
"""


SIZES = (500, 1000, 2000)
REPEATS = 5
SEED = 2026


def merge_sort(values):
    """Return a sorted copy using recursive stable merge sort."""
    if len(values) <= 1:
        return values[:]
    mid = len(values) // 2
    left = merge_sort(values[:mid])
    right = merge_sort(values[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # ties favor left: stability
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result


def quick_sort(values):
    """Return a sorted copy via in-place, first-pivot Lomuto quicksort.

    Uses an explicit stack instead of Python recursive calls, avoiding
    RecursionError on adverse inputs. Pivot policy is intentionally simple
    to reveal O(n^2) behavior on sorted and reverse-sorted sequences.
    """
    a = values[:]
    stack = [(0, len(a) - 1)] if a else []
    while stack:
        low, high = stack.pop()
        if low >= high:
            continue
        # Move the first element to the end for Lomuto partitioning.
        a[low], a[high] = a[high], a[low]
        pivot = a[high]
        border = low
        for j in range(low, high):
            if a[j] <= pivot:
                a[border], a[j] = a[j], a[border]
                border += 1
        a[border], a[high] = a[high], a[border]
        # Explicit stack represents the two recursive subproblems.
        stack.append((low, border - 1))
        stack.append((border + 1, high))
    return a


def make_input(kind, n):
    if kind == 'sorted':
        return list(range(n))
    if kind == 'reverse':
        return list(range(n - 1, -1, -1))
    rng = random.Random(SEED + n)
    return [rng.randrange(n * 10) for _ in range(n)]


def benchmark_one(fn, source):
    """Time and Python-allocation peak are measured in separate runs.

    The input list exists before measurement. Each function copies it.
    tracemalloc measures traced Python memory, NOT process RSS.
    """
    elapsed = []
    expected = sorted(source)
    for _ in range(REPEATS):
        start = time.perf_counter()
        result = fn(source)
        elapsed.append((time.perf_counter() - start) * 1000)
        assert result == expected
    tracemalloc.start()
    tracemalloc.reset_peak()
    result = fn(source)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert result == expected
    return round(statistics.median(elapsed), 4), round(peak / 1024, 2)


def main():
    print('Python:', platform.python_version(), '| System:', platform.system(), platform.machine())
    rows = []
    for n in SIZES:
        for kind in ('random', 'sorted', 'reverse'):
            source = make_input(kind, n)
            for name, fn in (('Merge Sort', merge_sort), ('Quick Sort', quick_sort)):
                ms, kib = benchmark_one(fn, source)
                row = dict(size=n, dataset=kind, algorithm=name, median_time_ms=ms, peak_traced_kib=kib)
                rows.append(row)
                print(row)
    path = Path(__file__).with_name('benchmarks.csv')
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print('Wrote:', path)


if __name__ == '__main__':
    main()
