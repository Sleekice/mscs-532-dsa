"""
Correctness tests for heapsort, the comparison sorts, and the priority queue.

Run from the assignment folder with either:
    python -m pytest tests
    python tests/test_algorithms.py
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from heapsort import heapsort, heapsort_comparisons  # noqa: E402
from priority_queue import PriorityQueue, Task  # noqa: E402
from sorting_algorithms import merge_sort, quicksort  # noqa: E402

def test_sorting_algorithms():
    rng = random.Random(1)
    cases = [[], [1], [2, 1], [3, 3, 3], list(range(100)), list(range(100, 0, -1)),
             [rng.randint(0, 5) for _ in range(300)], [rng.random() for _ in range(500)],
             ["kiwi", "apple", "fig", "apple"]]
    for case in cases:
        for fn in (heapsort, quicksort, merge_sort):
            assert fn(list(case)) == sorted(case), (fn.__name__, case)


def test_heapsort_comparisons_within_bound():
    import math
    rng = random.Random(2)
    for n in (100, 1000, 5000):
        data = [rng.random() for _ in range(n)]
        assert heapsort_comparisons(list(data)) <= 2 * n * math.log2(n)
    # All-equal keys: every sift-down stops at once, so O(n).
    assert heapsort_comparisons([7] * 1000) <= 3 * 1000


def test_priority_queue_random_operations():
    """Random inserts, key changes and extracts in both modes, checking the
    heap property and position map throughout."""
    rng = random.Random(1)
    for mode in ("max", "min"):
        pq = PriorityQueue(mode=mode)
        assert pq.is_empty()
        live = {}
        for step in range(3000):
            op = rng.random()
            if op < 0.5 or not live:
                t = Task(task_id=step, priority=rng.randint(0, 50), arrival_time=step)
                pq.insert(t)
                live[t.task_id] = t
            elif op < 0.75:
                t = live[rng.choice(list(live))]
                new = rng.randint(0, 50)
                pq.change_key(t, new)
            else:
                t = pq.extract()
                del live[t.task_id]
                best = max(live.values(), key=pq._rank, default=None)
                assert best is None or pq._rank(t) >= pq._rank(best)
            if step % 50 == 0:
                pq.check_invariants()
        # Draining gives sorted order.
        out = [pq.extract().priority for _ in range(len(pq))]
        assert out == sorted(out, reverse=(mode == "max"))
        assert pq.is_empty()


def test_priority_queue_api():
    pq = PriorityQueue("max")
    a, b, c = Task(1, 5), Task(2, 3), Task(3, 9)
    for t in (a, b, c):
        pq.insert(t)
    pq.increase_key(b, 10)
    assert pq.extract_max() is b
    pq.decrease_key(c, 1)
    assert pq.extract_max() is a and pq.extract_max() is c and pq.is_empty()
    for bad in (lambda: pq.extract(), lambda: pq.peek()):
        try:
            bad()
            raise AssertionError("expected IndexError")
        except IndexError:
            pass
    pq.insert(a)
    try:
        pq.increase_key(a, 0)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    try:
        pq.insert(a)
        raise AssertionError("expected ValueError for duplicate task")
    except ValueError:
        pass


def test_ties_are_first_come_first_served():
    pq = PriorityQueue("max")
    for i in range(10):
        pq.insert(Task(i, 1, arrival_time=i))
    assert [pq.extract().task_id for _ in range(10)] == list(range(10))


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print(f"PASS  {t.__name__}")
    print(f"All {len(tests)} tests passed.")
