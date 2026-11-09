import random
import unittest
from src.quicksort import randomized_quicksort, deterministic_quicksort
from src.hash_table import ChainedHashTable


class SortingTests(unittest.TestCase):
    def test_edge_cases(self):
        for data in ([], [7], [3, 3, 3, 3], list(range(100)),
                     list(range(99, -1, -1)), [5, -2, 4, -2, 0]):
            for sorter in (randomized_quicksort, deterministic_quicksort):
                original = data[:]
                self.assertEqual(sorter(data), sorted(data))
                self.assertEqual(data, original)

    def test_randomized_arrays(self):
        rng = random.Random(19)
        for n in (2, 3, 10, 100, 1000):
            items = [rng.randrange(-100, 100) for _ in range(n)]
            self.assertEqual(randomized_quicksort(items, random.Random(1)), sorted(items))
            self.assertEqual(deterministic_quicksort(items), sorted(items))


class HashTests(unittest.TestCase):
    def test_crud_and_resize(self):
        table = ChainedHashTable(capacity=3, seed=42)
        for k in range(1000):
            table.insert(k, str(k))
        self.assertEqual(len(table), 1000)
        self.assertLessEqual(table.load_factor, 0.75)
        for k in range(1000):
            self.assertEqual(table.search(k), str(k))
        table.insert(5, 'updated')
        self.assertEqual(table.search(5), 'updated')
        self.assertEqual(len(table), 1000)
        for k in range(1000):
            self.assertEqual(table.delete(k), 'updated' if k == 5 else str(k))
        self.assertEqual(len(table), 0)
        with self.assertRaises(KeyError):
            table.search(1001)
        with self.assertRaises(KeyError):
            table.delete(1001)

    def test_invalid_keys_and_collision(self):
        table = ChainedHashTable(capacity=2, seed=1)
        for k in (-4, 0, 4, 10**70):
            table.insert(k, k)
            self.assertEqual(table.search(k), k)
        with self.assertRaises(TypeError):
            table.insert('hello', 3)
        with self.assertRaises(ValueError):
            ChainedHashTable(max_load=1)


if __name__ == '__main__':
    unittest.main()
