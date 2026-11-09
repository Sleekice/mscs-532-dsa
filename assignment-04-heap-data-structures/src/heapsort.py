"""
Heapsort using an array-based binary max-heap.

    heapsort(arr)              sorts arr in place (ascending) and returns it
    heapsort_comparisons(arr)  same algorithm, returns the number of key comparisons
"""

def _sift_down(arr, start, end):
    """Restore the max-heap property for the subtree rooted at `start`,
    looking only at arr[0..end-1]. Iterative, so no recursion overhead.

    Instead of swapping at every level, we hold the root value aside and slide
    larger children up into the gap, then drop the value into its final spot.
    Same comparisons as the textbook MAX-HEAPIFY, about half the writes.
    """
    item = arr[start]
    pos = start
    child = 2 * pos + 1
    while child < end:
        right = child + 1
        if right < end and arr[right] > arr[child]:
            child = right
        if arr[child] <= item:
            break
        arr[pos] = arr[child]
        pos = child
        child = 2 * pos + 1
    arr[pos] = item


def heapsort(arr):
    """Sort arr in place in ascending order using a max-heap. Returns arr.

    Step 1, BUILD-MAX-HEAP: sift down every internal node, from the last one
            (index n//2 - 1) back to the root. This is O(n) overall.
    Step 2: repeatedly swap the max (arr[0]) into its final position at the
            end of the array, shrink the heap by one, and sift the new root
            down. n - 1 extractions at O(log n) each.
    """
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(arr, i, n)
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        _sift_down(arr, 0, end)
    return arr


def heapsort_comparisons(arr):
    """Same algorithm as heapsort(), but counts key comparisons.
    Kept separate so the timed version has no counting overhead."""
    count = 0

    def sift(start, end):
        nonlocal count
        item = arr[start]
        pos = start
        child = 2 * pos + 1
        while child < end:
            right = child + 1
            if right < end:
                count += 1
                if arr[right] > arr[child]:
                    child = right
            count += 1
            if arr[child] <= item:
                break
            arr[pos] = arr[child]
            pos = child
            child = 2 * pos + 1
        arr[pos] = item

    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        sift(i, n)
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        sift(0, end)
    return count
