from collections import deque
from typing import Optional


class Queue:
    """
    FIFO (First-In, First-Out) data structure backed by collections.deque.

    A queue supports three core O(1) operations:
      enqueue — add an element to the back
      dequeue — remove and return the element from the front
      peek    — inspect the front element without removing it

    Python's deque (double-ended queue) provides O(1) append (right end) and
    O(1) popleft (left end), making it the correct backing store for a queue.
    A plain list would give O(n) dequeue because list.pop(0) shifts all
    remaining elements.

    Operations and complexity:
      enqueue(x)  O(1) — deque.append
      dequeue()   O(1) — deque.popleft
      peek()      O(1) — index the leftmost element
      is_empty    O(1) — len check
      size        O(1) — len
    """

    def __init__(self) -> None:
        self._data: deque = deque()

    def enqueue(self, x) -> None:
        # Add the new element to the back (right end) of the deque.
        self._data.append(x)

    def dequeue(self) -> Optional[object]:
        # Remove and return the front (left end) element; return None if empty.
        return self._data.popleft() if self._data else None

    def peek(self) -> Optional[object]:
        # Return the front element without removing it; return None if empty.
        return self._data[0] if self._data else None

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)
