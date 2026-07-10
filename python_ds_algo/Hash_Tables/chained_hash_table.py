"""Hash table using separate chaining."""

from collections.abc import Iterator
from typing import TypeVar

from .hash_table import HashTable

K = TypeVar("K")
V = TypeVar("V")


class ChainedHashTable(HashTable[K, V]):
    """Resolve collisions with buckets; operations are O(1) expected, O(n) worst."""

    def _reset_storage(self, capacity: int) -> None:
        self._buckets: list[list[tuple[K, V]]] = [[] for _ in range(capacity)]

    def _bucket(self, key: K) -> list[tuple[K, V]]:
        return self._buckets[hash(key) % self._capacity]

    def _lookup(self, key: K) -> V:
        for stored_key, value in self._bucket(key):
            if stored_key == key:
                return value
        raise KeyError(key)

    def _store(self, key: K, value: V) -> None:
        bucket = self._bucket(key)
        for index, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                bucket[index] = (key, value)
                return
        bucket.append((key, value))

    def _delete(self, key: K) -> None:
        bucket = self._bucket(key)
        for index, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                bucket.pop(index)
                return
        raise KeyError(key)

    def _entries(self) -> Iterator[tuple[K, V]]:
        return (entry for bucket in self._buckets for entry in bucket)
