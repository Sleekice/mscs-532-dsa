"""Reproducible datasets; CSV output of median wall-clock timings."""
import argparse
import csv
import platform
import random
import statistics
import time
from pathlib import Path
from src.quicksort import randomized_quicksort, deterministic_quicksort
from src.hash_table import ChainedHashTable


def datasets(n: int, seed: int):
    rng = random.Random(seed)
    return {
        'random': [rng.randrange(0, 10 * n) for _ in range(n)],
        'sorted': list(range(n)),
        'reverse': list(range(n - 1, -1, -1)),
        'repeated': [rng.randrange(10) for _ in range(n)],
    }


def bench_sorts(sizes, repetitions: int, output: Path):
    rows = []
    for n in sizes:
        for distribution, values in datasets(n, seed=2300 + n).items():
            for algorithm in ('randomized', 'first_pivot'):
                times = []
                for r in range(repetitions):
                    start = time.perf_counter_ns()
                    if algorithm == 'randomized':
                        actual = randomized_quicksort(values, random.Random(19000 + r))
                    else:
                        actual = deterministic_quicksort(values)
                    elapsed = time.perf_counter_ns() - start
                    assert actual == sorted(values)
                    times.append(elapsed / 1_000_000)
                rows.append({'n': n, 'distribution': distribution,
                             'algorithm': algorithm, 'median_ms': round(statistics.median(times), 4),
                             'repetitions': repetitions})
    with output.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return rows


def bench_hash(sizes, repetitions, output: Path):
    rows = []
    for n in sizes:
        samples = {'insert': [], 'successful_search': [], 'delete': []}
        for r in range(repetitions):
            keys = random.Random(887 + r).sample(range(1, 20 * max(sizes)), n)
            table = ChainedHashTable(seed=120 + r)
            begin = time.perf_counter_ns()
            for key in keys:
                table.insert(key, key * 2)
            samples['insert'].append((time.perf_counter_ns() - begin) / n)
            begin = time.perf_counter_ns()
            for key in keys:
                assert table.search(key) == key * 2
            samples['successful_search'].append((time.perf_counter_ns() - begin) / n)
            begin = time.perf_counter_ns()
            for key in keys:
                assert table.delete(key) == key * 2
            samples['delete'].append((time.perf_counter_ns() - begin) / n)
            assert len(table) == 0
        for operation, values in samples.items():
            rows.append({'n': n, 'operation': operation,
                         'median_microseconds_per_op': round(statistics.median(values) / 1000, 4),
                         'repetitions': repetitions, 'max_load': 0.75})
    with output.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=int, nargs='+', default=[500, 1000, 2000, 4000])
    parser.add_argument('--repetitions', type=int, default=7)
    parser.add_argument('--output', type=Path, default=Path('results'))
    args = parser.parse_args()
    if min(args.sizes) < 1 or args.repetitions < 1:
        parser.error('positive sizes and repetitions required')
    args.output.mkdir(exist_ok=True, parents=True)
    sorts = bench_sorts(args.sizes, args.repetitions, args.output / 'quicksort.csv')
    hashing = bench_hash(args.sizes, args.repetitions, args.output / 'hashing.csv')
    (args.output / 'environment.txt').write_text(
        f'Python: {platform.python_version()}\nSystem: {platform.platform()}\n'
        f'Sizes: {args.sizes}\nRepetitions: {args.repetitions}\n'
        f'Timer: time.perf_counter_ns()\nStatistic: median\n')
    for row in sorts:
        print(row)
    for row in hashing:
        print(row)


if __name__ == '__main__':
    main()
