"""Idiomatic iteration, comprehension, and sorting examples."""

from collections.abc import Iterable, Sequence
from typing import TypeVar

T = TypeVar("T")


def indexed_pairs(values: Iterable[T]) -> list[tuple[int, T]]:
    """Pair positions and values in O(n) time and space using enumerate."""
    return list(enumerate(values))


def pairwise_totals(left: Iterable[int], right: Iterable[int]) -> list[int]:
    """Sum aligned items through the shorter input in O(min(n, m)) time."""
    return [a + b for a, b in zip(left, right)]


def transpose(matrix: Sequence[Sequence[T]]) -> list[list[T]]:
    """Transpose a rectangular matrix in O(rows * columns) time and space."""
    if not matrix:
        return []
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix must be rectangular")
    return [[matrix[row][column] for row in range(len(matrix))] for column in range(width)]


def unique_lengths(words: Iterable[str]) -> set[int]:
    """Return distinct word lengths in O(n) expected time and O(n) space."""
    return {len(word) for word in words}


def squares_by_parity(values: Iterable[int]) -> dict[str, list[int]]:
    """Group squared values using comprehensions in O(n) time and space."""
    materialized = list(values)
    return {label: [n * n for n in materialized if n % 2 == parity]
            for label, parity in (("even", 0), ("odd", 1))}


def boundary_truth(values: Iterable[bool]) -> tuple[bool, bool]:
    """Return any/all results in O(n) time and O(1) extra space."""
    materialized = list(values)
    return any(materialized), all(materialized)


def stable_rank(records: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """Sort score descending and name ascending without mutation in O(n log n)."""
    return sorted(records, key=lambda record: (-record[1], record[0]))


def sort_in_place(values: list[T]) -> None:
    """Mutate a list into ascending order in O(n log n) time."""
    values.sort()
