"""Custom iterators and lazy generator utilities."""

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")
_MISSING = object()


class Countdown(Iterator[int]):
    """Single-use iterator yielding n through 1 in O(n) total time."""

    def __init__(self, start: int) -> None:
        if start < 0:
            raise ValueError("start cannot be negative")
        self._next = start

    def __iter__(self) -> "Countdown":
        return self

    def __next__(self) -> int:
        if self._next == 0:
            raise StopIteration
        value = self._next
        self._next -= 1
        return value


class Peekable(Iterator[T], Generic[T]):
    """Add O(1) lookahead and space to any iterator."""

    def __init__(self, values: Iterable[T]) -> None:
        self._iterator = iter(values)
        self._buffer: T | object = _MISSING

    def __iter__(self) -> "Peekable[T]":
        return self

    def peek(self) -> T:
        if self._buffer is _MISSING:
            self._buffer = next(self._iterator)
        return self._buffer  # type: ignore[return-value]

    def __next__(self) -> T:
        if self._buffer is not _MISSING:
            value = self._buffer
            self._buffer = _MISSING
            return value  # type: ignore[return-value]
        return next(self._iterator)


def chunked(values: Iterable[T], size: int) -> Iterator[list[T]]:
    """Lazily yield lists of at most size in O(n) time and O(size) space."""
    if size <= 0:
        raise ValueError("size must be positive")
    iterator = iter(values)
    while True:
        chunk: list[T] = []
        try:
            for _ in range(size):
                chunk.append(next(iterator))
        except StopIteration:
            if chunk:
                yield chunk
            return
        yield chunk


def flatten(values: Iterable[T | Iterable[T]]) -> Iterator[T]:
    """Recursively flatten non-string iterables in O(n) time and O(depth) space."""
    for value in values:
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            yield from flatten(value)
        else:
            yield value  # type: ignore[misc]
