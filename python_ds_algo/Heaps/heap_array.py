# Min-Heap — Array-Based Implementation
#
# Concept: A complete binary tree stored implicitly in a list. The shape of
# the tree is encoded by index arithmetic rather than pointers:
#
#   Parent of i   : (i - 1) // 2
#   Left child    : 2 * i + 1
#   Right child   : 2 * i + 2
#
# The heap property: every node is <= its children (min-heap), so the
# smallest element is always at index 0.
#
# Why arrays beat explicit tree nodes for heaps:
#   - No pointer overhead; the whole heap fits in one contiguous block.
#   - Cache-friendly: parent/child access patterns stay local in memory.
#   - Index arithmetic is O(1) and branchless.
#
# Operations and complexity:
#   push(x)   O(log n) — append then sift up
#   pop()     O(log n) — replace root with last element then sift down
#   peek()    O(1)     — read index 0
#   heapify   O(n)     — Floyd's bottom-up build (see heapify_and_heapsort.py)

from typing import List, Optional


class MinHeapArray:
    def __init__(self) -> None:
        self._data: List[int] = []

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def push(self, val: int) -> None:
        # Append to the end (maintaining the complete-tree shape) then
        # restore the heap property by sifting the new element up.
        self._data.append(val)
        self._sift_up(len(self._data) - 1)

    def pop(self) -> Optional[int]:
        if not self._data:
            return None
        # Swap the root (minimum) with the last element so we can remove
        # it cheaply, then sift the new root down to restore order.
        self._swap(0, len(self._data) - 1)
        min_val = self._data.pop()
        if self._data:
            self._sift_down(0)
        return min_val

    def peek(self) -> Optional[int]:
        return self._data[0] if self._data else None

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sift_up(self, i: int) -> None:
        # Walk up the tree while the current node is smaller than its parent.
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i] < self._data[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        # Walk down the tree, swapping with the smaller child until the
        # heap property holds.
        n = len(self._data)
        while True:
            smallest = i
            left  = 2 * i + 1
            right = 2 * i + 2
            if left  < n and self._data[left]  < self._data[smallest]:
                smallest = left
            if right < n and self._data[right] < self._data[smallest]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def _swap(self, i: int, j: int) -> None:
        self._data[i], self._data[j] = self._data[j], self._data[i]
