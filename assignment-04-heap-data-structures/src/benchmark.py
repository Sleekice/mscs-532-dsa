"""
Runs the experiments and saves the raw results to ../results/.

    1. Sorting benchmark: heapsort vs randomized quicksort vs merge sort on
       random, sorted, reverse-sorted and few-unique-values input, plus
       heapsort comparison counts.
    2. Scheduler simulation: FIFO, Priority, Priority + aging, EDF.

Run from the assignment folder:
    python src/benchmark.py           # full run (~20 seconds)
    python src/benchmark.py --quick   # smaller sizes, a few seconds
Then draw the chart with:
    python src/plot_results.py
"""

import csv
import gc
import io
import math
import os
import platform
import random
import sys
import time
from contextlib import redirect_stdout

from heapsort import heapsort, heapsort_comparisons
from scheduler import POLICIES, run_scheduler
from sorting_algorithms import merge_sort, quicksort

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")

DISTRIBUTIONS = ["Random", "Sorted", "Reverse-sorted", "Few unique values"]
ALGORITHMS = {"Heapsort": heapsort, "Quicksort (randomized)": quicksort, "Merge sort": merge_sort}


def make_input(kind, n, rng):
    if kind == "Random":
        return [rng.random() for _ in range(n)]
    if kind == "Sorted":
        return sorted(rng.random() for _ in range(n))
    if kind == "Reverse-sorted":
        return sorted((rng.random() for _ in range(n)), reverse=True)
    if kind == "Few unique values":
        return [rng.randint(0, 9) for _ in range(n)]
    raise ValueError(kind)


def time_sort(fn, data, repeats):
    """Best of `repeats` runs with the garbage collector paused. The minimum is
    the run with the least interference from the rest of the machine, which is
    what Python's timeit documentation recommends."""
    times = []
    gc.disable()
    try:
        for _ in range(repeats):
            arr = list(data)
            t0 = time.perf_counter()
            fn(arr)
            times.append(time.perf_counter() - t0)
    finally:
        gc.enable()
    return min(times)


def benchmark_sorts(sizes, repeats):
    """Returns a list of rows: distribution, n, one time per algorithm (ms),
    heapsort comparisons, comparisons / (n log2 n)."""
    rng = random.Random(42)
    rows = []
    print(f"{'Input':<20}{'n':>8}" + "".join(f"{a:>25}" for a in ALGORITHMS) + f"{'heap cmp / n log2 n':>22}")
    for kind in DISTRIBUTIONS:
        for n in sizes:
            data = make_input(kind, n, rng)
            row = {"distribution": kind, "n": n}
            line = f"{kind:<20}{n:>8}"
            for name, fn in ALGORITHMS.items():
                ms = time_sort(fn, data, repeats) * 1000
                row[name] = round(ms, 3)
                line += f"{ms:>22.2f} ms"
            comps = heapsort_comparisons(list(data))
            row["heapsort_comparisons"] = comps
            row["comparisons_per_nlogn"] = round(comps / (n * math.log2(n)), 4)
            print(line + f"{row['comparisons_per_nlogn']:>22.3f}")
            rows.append(row)
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    quick = "--quick" in sys.argv
    if quick:
        sizes, repeats, n_tasks = [1000, 2000, 4000, 8000], 2, 1000
    else:
        sizes, repeats, n_tasks = [1000, 2000, 4000, 8000, 16000, 32000, 64000], 5, 5000
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Everything printed goes to the screen and to benchmark_console.txt.
    buf = io.StringIO()

    class Tee(io.TextIOBase):
        def write(self, s):
            sys.__stdout__.write(s)
            buf.write(s)
            return len(s)

    with redirect_stdout(Tee()):
        print(f"Sorting benchmark (time = best of {repeats} runs, milliseconds)\n")
        sort_rows = benchmark_sorts(sizes, repeats)
        sched = run_scheduler(n_tasks)

    write_csv(os.path.join(RESULTS_DIR, "sorting.csv"), sort_rows)
    sched_rows = []
    for policy in POLICIES:
        s = sched[policy]
        row = {"policy": policy, "avg_wait": round(s["avg_wait"], 3), "p95_wait": round(s["p95_wait"], 3),
               "max_wait": round(s["max_wait"], 3), "deadline_miss_rate": round(s["miss_rate"], 4)}
        for p in range(5, 0, -1):
            row[f"avg_wait_P{p}"] = round(s["wait_by_priority"][p], 3)
        sched_rows.append(row)
    write_csv(os.path.join(RESULTS_DIR, "scheduler.csv"), sched_rows)

    with open(os.path.join(RESULTS_DIR, "benchmark_console.txt"), "w") as f:
        f.write(buf.getvalue())
    with open(os.path.join(RESULTS_DIR, "environment.txt"), "w") as f:
        f.write(f"Python: {sys.version}\n")
        f.write(f"Implementation: {platform.python_implementation()}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Processor: {platform.processor() or platform.machine()}\n")
        f.write(f"Mode: {'quick' if quick else 'full'}\n")
        f.write(f"Sizes: {sizes}\nRepeats: {repeats}\nScheduler tasks: {n_tasks}\n")
    print(f"\nSaved sorting.csv, scheduler.csv, benchmark_console.txt and environment.txt to results/")
    print("Run `python src/plot_results.py` to draw the chart.")


if __name__ == "__main__":
    main()
