"""Hash table using linear probing and tombstones."""

from collections.abc import Iterator
from typing import TypeVar, cast

from .hash_table import HashTable

K = TypeVar("K")
V = TypeVar("V")
_EMPTY = object()
_DELETED = object()


class LinearProbingHashTable(HashTable[K, V]):
    """Resolve collisions by probing; operations are O(1) expected, O(n) worst."""

    def _reset_storage(self, capacity: int) -> None:
        self._slots: list[object] = [_EMPTY] * capacity

    def _probe(self, key: K) -> Iterator[int]:
        start = hash(key) % self._capacity
        for offset in range(self._capacity):
            yield (start + offset) % self._capacity

    def _lookup(self, key: K) -> V:
        for index in self._probe(key):
            slot = self._slots[index]
            if slot is _EMPTY:
                break
            if slot is not _DELETED:
                stored_key, value = cast(tuple[K, V], slot)
                if stored_key == key:
                    return value
        raise KeyError(key)

    def _store(self, key: K, value: V) -> None:
        first_deleted: int | None = None
        for index in self._probe(key):
            slot = self._slots[index]
            if slot is _DELETED and first_deleted is None:
                first_deleted = index
            elif slot is _EMPTY:
                self._slots[first_deleted if first_deleted is not None else index] = (key, value)
                return
            else:
                stored_key, _ = cast(tuple[K, V], slot)
                if stored_key == key:
                    self._slots[index] = (key, value)
                    return
        if first_deleted is not None:
            self._slots[first_deleted] = (key, value)
            return
        raise RuntimeError("hash table has no free slot")

    def _delete(self, key: K) -> None:
        for index in self._probe(key):
            slot = self._slots[index]
            if slot is _EMPTY:
                break
            if slot is not _DELETED and cast(tuple[K, V], slot)[0] == key:
                self._slots[index] = _DELETED
                return
        raise KeyError(key)

    def _entries(self) -> Iterator[tuple[K, V]]:
        return (cast(tuple[K, V], slot) for slot in self._slots if slot not in (_EMPTY, _DELETED))
