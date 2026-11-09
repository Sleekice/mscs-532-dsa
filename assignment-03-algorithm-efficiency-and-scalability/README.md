# UC MSCS 532 — Assignment 3: Algorithm Efficiency and Scalability

**Peter Nwochie Tiewah** | University of the Cumberlands | MSCS 532

This project compares randomized and first-element-pivot Quicksort and implements a chained hash table with universal hashing and dynamic resizing. Benchmark results below come from my Mac, running Python 3.15.2, with seven timing repetitions per case.

## Project files

- `src/quicksort.py` — iterative three-way Quicksort; sorted copies, randomized or first pivot.
- `src/hash_table.py` — integer-key chained hash table with insert, search, delete, and growth above a load factor of 0.75.
- `src/benchmark.py` — reproducible test datasets and performance measurements.
- `src/plot_results.py` — generates the sorting comparison chart from the CSV file (requires Matplotlib).
- `tests/test_algorithms.py` — sorting and hash table correctness tests.
- `results/quicksort.csv` — 32 sorting measurements from the Mac run.
- `results/hashing.csv` — 12 hash table measurements from the Mac run.
- `results/environment.txt` — interpreter and benchmark parameters (regenerate locally for exact OS details).
- `results/benchmark_console.txt` — saved benchmark console text; regenerate with the `tee` command below.
- `results/quicksort_comparison.png` — figure generated from `quicksort.csv`.
- `Assignment_3_Report_Peter_Tiewah.docx` — analysis, results and references in Word format.

## Requirements

Python 3.10 or newer for the core scripts; used **Python 3.15.2 on macOS** for the submitted measurements. The sorting, hashing and tests use Python's standard library. **Matplotlib is only needed to regenerate the plot.**

## Run from the Assignment 3 folder

```bash
python --version
python -m unittest discover -s tests -v
python -m src.benchmark | tee results/benchmark_console.txt
python -m pip install matplotlib
python -m src.plot_results
```

The test command checks correctness; the benchmark measures runtime. `python -m src.benchmark` regenerates `results/environment.txt`, `results/quicksort.csv`, and `results/hashing.csv`, but **does not** regenerate `benchmark_console.txt` unless piped through `tee`. It also **does not** regenerate `quicksort_comparison.png`; run `python -m src.plot_results` separately. Re-running measurements may change the values and should be followed by a review of the Word report.

To specify experimental sizes and repetitions:

```bash
python -m src.benchmark --sizes 500 1000 2000 4000 --repetitions 7 | tee results/benchmark_console.txt
python -m src.plot_results
```

## Small example

```python
from src.quicksort import randomized_quicksort, deterministic_quicksort
from src.hash_table import ChainedHashTable

numbers = [8, 3, 3, 9, 1]
print(randomized_quicksort(numbers))       # [1, 3, 3, 8, 9]
print(deterministic_quicksort(numbers))    # [1, 3, 3, 8, 9]

table = ChainedHashTable(capacity=11, seed=42)
table.insert(101, "student A")
print(table.search(101))                   # student A
table.insert(101, "updated")
print(table.delete(101))                   # updated
```

An absent key raises `KeyError` for search/delete; non-integer keys raise `TypeError`.

## Findings from the Mac run

At `n = 4,000`, randomized Quicksort took **2.4047 ms** on reverse-sorted data versus **229.4699 ms** for first-pivot Quicksort (about **95.4×** as long). On random data, first-pivot Quicksort was faster (**2.0864 ms** versus **2.5791 ms**). Both methods handled repeated keys efficiently because the three-way partition groups identical elements. Successful hash-table searches ranged from **0.1878 to 0.2032 µs per operation** at load factors capped at 0.75. See the Word report for the full analysis and its limitations.

## Submission

This folder belongs inside the existing `mscs-532-dsa` GitHub repository alongside Assignment 2. Commit the source, tests, results, README and Word report; do **not** commit `.venv` or `.venv315` environments. Submit your repository URL in Canvas.
