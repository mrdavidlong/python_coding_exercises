"""A resizable array implementing Python's mutable-sequence protocol."""

from collections.abc import Iterable, MutableSequence
from typing import Generic, TypeVar, overload

T = TypeVar("T")


class DynamicArray(MutableSequence[T], Generic[T]):
    """Store values in a geometrically growing buffer.

    Indexed access and assignment are O(1). Appending is amortized O(1), while
    insertion and deletion are O(n). The allocated buffer uses O(capacity)
    space and never shrinks automatically.
    """

    def __init__(self, values: Iterable[T] = (), *, initial_capacity: int = 1) -> None:
        if not isinstance(initial_capacity, int) or isinstance(initial_capacity, bool):
            raise TypeError("initial_capacity must be an integer")
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be positive")
        self._capacity = initial_capacity
        self._size = 0
        self._items: list[T | None] = [None] * self._capacity
        self.extend(values)

    @property
    def capacity(self) -> int:
        """Return allocated slots in O(1) time."""
        return self._capacity

    def __len__(self) -> int:
        return self._size

    def _index(self, index: int) -> int:
        if not isinstance(index, int):
            raise TypeError("indices must be integers or slices")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("dynamic array index out of range")
        return index

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> list[T]: ...

    def __getitem__(self, index: int | slice) -> T | list[T]:
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(self._size))]
        value = self._items[self._index(index)]
        return value  # type: ignore[return-value]

    def __setitem__(self, index: int, value: T) -> None:
        self._items[self._index(index)] = value

    def __delitem__(self, index: int) -> None:
        index = self._index(index)
        for position in range(index, self._size - 1):
            self._items[position] = self._items[position + 1]
        self._size -= 1
        self._items[self._size] = None

    def insert(self, index: int, value: T) -> None:
        """Insert before *index* in O(n), using list-style index clamping."""
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0:
            index = max(0, self._size + index)
        else:
            index = min(index, self._size)
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        for position in range(self._size, index, -1):
            self._items[position] = self._items[position - 1]
        self._items[index] = value
        self._size += 1

    def _resize(self, capacity: int) -> None:
        new_items: list[T | None] = [None] * capacity
        new_items[: self._size] = self._items[: self._size]
        self._items = new_items
        self._capacity = capacity
