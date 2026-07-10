"""Fenwick tree (binary indexed tree) for cumulative sums."""

from collections.abc import Iterable


class FenwickTree:
    """Support point additions and inclusive range sums.

    Construction is O(n), updates and queries are O(log n), and storage is
    O(n). Public indexes are zero-based; the internal tree is one-based so
    ``index & -index`` isolates the least-significant set bit used to move
    between a node and the range that contains or precedes it.
    """

    def __init__(self, values: Iterable[int] = ()) -> None:
        materialized = list(values)
        self._size = len(materialized)
        self._tree = [0] + materialized
        for index in range(1, self._size + 1):
            parent = index + (index & -index)
            if parent <= self._size:
                self._tree[parent] += self._tree[index]

    def __len__(self) -> int:
        return self._size

    def _validate_index(self, index: int) -> None:
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("index must be an integer")
        if index < 0 or index >= self._size:
            raise IndexError("Fenwick tree index out of range")

    def add(self, index: int, delta: int) -> None:
        """Add delta to one value in O(log n) time."""
        self._validate_index(index)
        internal = index + 1
        while internal <= self._size:
            self._tree[internal] += delta
            internal += internal & -internal

    def prefix_sum(self, index: int) -> int:
        """Return the inclusive sum from zero through index in O(log n) time."""
        self._validate_index(index)
        total = 0
        internal = index + 1
        while internal:
            total += self._tree[internal]
            internal -= internal & -internal
        return total

    def range_sum(self, start: int, end: int) -> int:
        """Return the inclusive sum from start through end in O(log n) time."""
        self._validate_index(start)
        self._validate_index(end)
        if start > end:
            raise ValueError("start cannot exceed end")
        return self.prefix_sum(end) - (self.prefix_sum(start - 1) if start else 0)
