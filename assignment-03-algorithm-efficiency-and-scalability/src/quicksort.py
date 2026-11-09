"""Iterative three-way Quicksort with uniformly random or first-element pivots."""
import random
from typing import List


def quicksort(values: List[int], *, randomized: bool = True,
              rng: random.Random | None = None) -> List[int]:
    """Return a sorted copy; never mutate the caller's list.

    A uniform pivot is chosen from each active subarray when randomized=True.
    Dutch-national-flag partitioning places values <, ==, > the pivot in
    three regions; this prevents repeated keys from causing quadratic work.
    An explicit stack prevents Python recursion-limit failures.
    """
    result = list(values)
    if len(result) < 2:
        return result
    rng = rng if rng is not None else random.Random()
    stack = [(0, len(result) - 1)]
    while stack:
        low, high = stack.pop()
        while low < high:
            pivot_index = rng.randrange(low, high + 1) if randomized else low
            pivot = result[pivot_index]
            lt, i, gt = low, low, high
            while i <= gt:
                if result[i] < pivot:
                    result[lt], result[i] = result[i], result[lt]
                    lt += 1
                    i += 1
                elif result[i] > pivot:
                    result[i], result[gt] = result[gt], result[i]
                    gt -= 1
                else:
                    i += 1
            # Process smaller side locally, pushing the larger side.
            if lt - low < high - gt:
                if gt + 1 < high:
                    stack.append((gt + 1, high))
                high = lt - 1
            else:
                if low < lt - 1:
                    stack.append((low, lt - 1))
                low = gt + 1
    return result


def randomized_quicksort(values: List[int], rng: random.Random | None = None) -> List[int]:
    return quicksort(values, randomized=True, rng=rng)


def deterministic_quicksort(values: List[int]) -> List[int]:
    return quicksort(values, randomized=False)
