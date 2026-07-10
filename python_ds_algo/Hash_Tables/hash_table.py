"""Shared template for hash tables with interchangeable collision handling."""

from abc import ABC, abstractmethod
from collections.abc import Iterator, MutableMapping
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class HashTable(MutableMapping[K, V], ABC, Generic[K, V]):
    """Provide resizing and mapping behavior for collision strategies.

    Subclasses provide expected O(1) lookup, storage, and deletion hooks.
    Resizing takes O(n) time and the table occupies O(capacity + n) space.
    """

    def __init__(self, capacity: int = 8, *, max_load_factor: float = 0.75) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise TypeError("capacity must be an integer")
        if capacity < 2:
            raise ValueError("capacity must be at least 2")
        if not 0 < max_load_factor <= 1:
            raise ValueError("max_load_factor must be in (0, 1]")
        self._capacity = capacity
        self._max_load_factor = max_load_factor
        self._size = 0
        self._reset_storage(capacity)

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def load_factor(self) -> float:
        return self._size / self._capacity

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, key: K) -> V:
        return self._lookup(key)

    def __setitem__(self, key: K, value: V) -> None:
        try:
            self._lookup(key)
        except KeyError:
            if (self._size + 1) / self._capacity > self._max_load_factor:
                self._resize(self._capacity * 2)
            self._store(key, value)
            self._size += 1
        else:
            self._store(key, value)

    def __delitem__(self, key: K) -> None:
        self._delete(key)
        self._size -= 1

    def __iter__(self) -> Iterator[K]:
        return self._keys()

    def _resize(self, capacity: int) -> None:
        entries = list(self._entries())
        self._capacity = capacity
        self._reset_storage(capacity)
        for key, value in entries:
            self._store(key, value)

    @abstractmethod
    def _reset_storage(self, capacity: int) -> None: ...

    @abstractmethod
    def _lookup(self, key: K) -> V: ...

    @abstractmethod
    def _store(self, key: K, value: V) -> None: ...

    @abstractmethod
    def _delete(self, key: K) -> None: ...

    @abstractmethod
    def _entries(self) -> Iterator[tuple[K, V]]: ...

    def _keys(self) -> Iterator[K]:
        return (key for key, _ in self._entries())
