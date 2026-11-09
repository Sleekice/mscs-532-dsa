"""Integer-key hash table with chaining, universal hashing, and resizing."""
import random
from typing import Any


class ChainedHashTable:
    """Map integer keys to values via buckets of (key, value) pairs.

    Hash family: h_{a,b}(k) = ((a*(k mod p)+b) mod p) mod m,
    with p prime, a in [1,p-1], b in [0,p-1].
    Assumes integer keys with 0 <= key < p for universal-family guarantee.
    Larger or negative integers remain supported functionally, but that
    theoretical guarantee does not directly apply to their reduction mod p.
    """
    PRIME = 2**61 - 1

    def __init__(self, capacity: int = 11, max_load: float = 0.75,
                 seed: int | None = None):
        if capacity < 2:
            raise ValueError('capacity must be >= 2')
        if not (0 < max_load < 1):
            raise ValueError('max_load must be strictly between 0 and 1')
        self._rng = random.Random(seed)
        self._a = self._rng.randrange(1, self.PRIME)
        self._b = self._rng.randrange(self.PRIME)
        self._buckets: list[list[tuple[int, Any]]] = [[] for _ in range(capacity)]
        self._size = 0
        self._max_load = max_load

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        return self._size / self.capacity

    def _index(self, key: int) -> int:
        if type(key) is not int:
            raise TypeError('keys must be integers')
        return ((self._a * (key % self.PRIME) + self._b) % self.PRIME) % self.capacity

    def _resize(self, new_capacity: int) -> None:
        old = self._buckets
        self._buckets = [[] for _ in range(new_capacity)]
        self._size = 0
        for bucket in old:
            for key, value in bucket:
                self._insert_no_resize(key, value)

    def _insert_no_resize(self, key: int, value: Any) -> None:
        self._buckets[self._index(key)].append((key, value))
        self._size += 1

    def insert(self, key: int, value: Any) -> None:
        index = self._index(key)
        bucket = self._buckets[index]
        for i, (old_key, _) in enumerate(bucket):
            if old_key == key:
                bucket[i] = (key, value)
                return
        if (self._size + 1) / self.capacity > self._max_load:
            self._resize(self.capacity * 2 + 1)
            index = self._index(key)
        self._buckets[index].append((key, value))
        self._size += 1

    def search(self, key: int) -> Any:
        for existing_key, value in self._buckets[self._index(key)]:
            if existing_key == key:
                return value
        raise KeyError(key)

    def delete(self, key: int) -> Any:
        bucket = self._buckets[self._index(key)]
        for i, (existing_key, value) in enumerate(bucket):
            if existing_key == key:
                bucket.pop(i)
                self._size -= 1
                return value
        raise KeyError(key)
