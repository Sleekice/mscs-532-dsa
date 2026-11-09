"""
Sorting algorithms used as a baseline for comparison with heapsort.

    quicksort(arr)   randomized quicksort, Hoare partition, iterative
    merge_sort(arr)  bottom-up merge sort with one auxiliary buffer
"""

import random

def quicksort(arr, rng=random):
    """Randomized quicksort, Hoare partition, explicit stack (no recursion
    limit problems). Sorts in place and returns arr."""
    if len(arr) < 2:
        return arr
    stack = [(0, len(arr) - 1)]
    while stack:
        lo, hi = stack.pop()
        while lo < hi:
            p = rng.randint(lo, hi)
            arr[lo], arr[p] = arr[p], arr[lo]
            pivot = arr[lo]
            i, j = lo - 1, hi + 1
            while True:
                i += 1
                while arr[i] < pivot:
                    i += 1
                j -= 1
                while arr[j] > pivot:
                    j -= 1
                if i >= j:
                    break
                arr[i], arr[j] = arr[j], arr[i]
            # j is the split point: arr[lo..j] <= arr[j+1..hi]
            if j - lo < hi - j:
                stack.append((j + 1, hi))
                hi = j
            else:
                stack.append((lo, j))
                lo = j + 1
    return arr


def merge_sort(arr):
    """Bottom-up merge sort with one auxiliary buffer. Stable. Returns arr
    sorted (the contents of arr are replaced in place)."""
    n = len(arr)
    if n < 2:
        return arr
    src, dst = arr, [None] * n
    width = 1
    while width < n:
        for lo in range(0, n, 2 * width):
            mid = min(lo + width, n)
            hi = min(lo + 2 * width, n)
            i, j, k = lo, mid, lo
            while i < mid and j < hi:
                if src[j] < src[i]:
                    dst[k] = src[j]
                    j += 1
                else:
                    dst[k] = src[i]
                    i += 1
                k += 1
            if i < mid:
                dst[k:hi] = src[i:mid]
            elif j < hi:
                dst[k:hi] = src[j:hi]
        src, dst = dst, src
        width *= 2
    if src is not arr:
        arr[:] = src
    return arr
