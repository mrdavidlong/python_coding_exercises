from typing import Optional


class Stack:
    """
    LIFO (Last-In, First-Out) data structure backed by a Python list.

    A stack supports three core O(1) operations:
      push  — add an element to the top
      pop   — remove and return the top element
      peek  — inspect the top element without removing it

    Python list append/pop(-1) are both amortized O(1), making a list the
    natural backing store. All operations are in-place; no extra memory
    beyond the stored elements is needed.

    Operations and complexity:
      push(x)   O(1) amortized — list.append
      pop()     O(1) amortized — list.pop
      peek()    O(1)           — index the last element
      is_empty  O(1)           — len check
      size      O(1)           — len
    """

    def __init__(self) -> None:
        self._data: list = []

    def push(self, x) -> None:
        # Append to the end of the list; this is the "top" of the stack.
        self._data.append(x)

    def pop(self) -> Optional[object]:
        # Remove and return the top element; return None if empty.
        return self._data.pop() if self._data else None

    def peek(self) -> Optional[object]:
        # Return the top element without removing it; return None if empty.
        return self._data[-1] if self._data else None

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)
