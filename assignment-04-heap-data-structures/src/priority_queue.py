"""
Priority queue implemented as an array-based binary heap, and the Task class
it stores.

    PriorityQueue(mode="max", key="priority")
        insert(task)                 O(log n)
        extract_max() / extract_min()  O(log n)
        increase_key(task, value)    O(log n)
        decrease_key(task, value)    O(log n)
        peek(), is_empty(), len()    O(1)
"""

import math
from dataclasses import dataclass, field

# ===========================================================================
#
# Representation: a plain Python list used as an implicit complete binary tree.
#   parent(i) = (i - 1) // 2,  left(i) = 2i + 1,  right(i) = 2i + 2
# No node objects or pointers, so it is compact and cache friendly, and since
# a heap is always a complete tree, the list never has holes. Appending to the
# end and popping from the end are amortized O(1), which is exactly what
# insert and extract need.
#
# To support increase_key / decrease_key in O(log n) we also keep a dictionary
# task_id -> index in the list. Without it, finding the task would be an O(n)
# scan. Every swap updates the dictionary.
#
# The queue can run as a max-heap (largest key served first) or a min-heap
# (smallest key first), and the key is any numeric attribute of Task. The
# scheduler uses:
#     max-heap on `priority`       for priority scheduling (bigger = more urgent)
#     min-heap on `deadline`       for Earliest Deadline First
#     min-heap on `arrival_time`   for FIFO, which shows a heap can do that too
# Ties are broken by earlier arrival time, then lower task_id, so tasks with
# equal keys come out in first-come, first-served order.


@dataclass
class Task:
    task_id: int
    priority: int
    arrival_time: float = 0.0
    duration: float = 1.0
    deadline: float = math.inf
    name: str = ""
    # Filled in by the scheduler
    base_priority: int = field(default=None)
    start_time: float = None
    finish_time: float = None
    last_aged: float = None

    def __post_init__(self):
        if self.base_priority is None:
            self.base_priority = self.priority
        if self.last_aged is None:
            self.last_aged = self.arrival_time

    @property
    def waiting_time(self):
        return None if self.start_time is None else self.start_time - self.arrival_time

    @property
    def missed_deadline(self):
        return self.finish_time is not None and self.finish_time > self.deadline


class PriorityQueue:
    def __init__(self, mode="max", key="priority"):
        if mode not in ("max", "min"):
            raise ValueError("mode must be 'max' or 'min'")
        self.mode = mode
        self.key = key
        self._heap = []
        self._pos = {}  # task_id -> index in self._heap

    # ---- ordering ---------------------------------------------------------
    def _rank(self, task):
        """Bigger rank means closer to the root."""
        k = getattr(task, self.key)
        return (k if self.mode == "max" else -k, -task.arrival_time, -task.task_id)

    def _above(self, i, j):
        """True if the task at index i should sit above the task at index j."""
        return self._rank(self._heap[i]) > self._rank(self._heap[j])

    def _swap(self, i, j):
        h = self._heap
        h[i], h[j] = h[j], h[i]
        self._pos[h[i].task_id] = i
        self._pos[h[j].task_id] = j

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if not self._above(i, parent):
                break
            self._swap(i, parent)
            i = parent
        return i

    def _sift_down(self, i):
        n = len(self._heap)
        while True:
            best = i
            left, right = 2 * i + 1, 2 * i + 2
            if left < n and self._above(left, best):
                best = left
            if right < n and self._above(right, best):
                best = right
            if best == i:
                return i
            self._swap(i, best)
            i = best

    # ---- core operations --------------------------------------------------
    def insert(self, task):
        """Add a task. O(log n): append at the bottom, then sift up."""
        if task.task_id in self._pos:
            raise ValueError(f"task {task.task_id} is already in the queue")
        self._heap.append(task)
        self._pos[task.task_id] = len(self._heap) - 1
        self._sift_up(len(self._heap) - 1)

    def peek(self):
        """Return the top task without removing it. O(1)."""
        if not self._heap:
            raise IndexError("peek from an empty priority queue")
        return self._heap[0]

    def extract(self):
        """Remove and return the top task. O(log n): move the last task to
        the root, then sift it down."""
        if not self._heap:
            raise IndexError("extract from an empty priority queue")
        top = self._heap[0]
        last = self._heap.pop()
        del self._pos[top.task_id]
        if self._heap:
            self._heap[0] = last
            self._pos[last.task_id] = 0
            self._sift_down(0)
        return top

    def extract_max(self):
        if self.mode != "max":
            raise TypeError("extract_max() on a min-heap; use extract_min()")
        return self.extract()

    def extract_min(self):
        if self.mode != "min":
            raise TypeError("extract_min() on a max-heap; use extract_max()")
        return self.extract()

    def change_key(self, task, new_value):
        """Set the task's key to new_value and move it to its correct place.
        O(log n): O(1) lookup in the position map, then one sift. Only one of
        the two sifts can actually move the task."""
        i = self._pos.get(task.task_id)
        if i is None:
            raise KeyError(f"task {task.task_id} is not in the queue")
        setattr(self._heap[i], self.key, new_value)
        i = self._sift_up(i)
        self._sift_down(i)

    def increase_key(self, task, new_value):
        """Raise the task's key. In a max-heap this can only move it up."""
        if new_value < getattr(task, self.key):
            raise ValueError("new key is smaller than the current key")
        self.change_key(task, new_value)

    def decrease_key(self, task, new_value):
        """Lower the task's key. In a min-heap this can only move it up."""
        if new_value > getattr(task, self.key):
            raise ValueError("new key is larger than the current key")
        self.change_key(task, new_value)

    def is_empty(self):
        return not self._heap

    def __len__(self):
        return len(self._heap)

    def __contains__(self, task):
        return task.task_id in self._pos

    def tasks(self):
        """Snapshot of the queued tasks (in heap order, not sorted)."""
        return list(self._heap)

    def check_invariants(self):
        """Used by the tests: heap property holds and the position map is right."""
        for i, t in enumerate(self._heap):
            assert self._pos[t.task_id] == i
            for c in (2 * i + 1, 2 * i + 2):
                if c < len(self._heap):
                    assert not self._above(c, i), "heap property violated"
        assert len(self._pos) == len(self._heap)
