"""Small examples that make mutation and copying behavior explicit."""

from copy import deepcopy
from typing import TypeVar

T = TypeVar("T")


def alias(values: list[T]) -> list[T]:
    """Return the same object in O(1) time and space."""
    return values


def shallow_copy(values: list[T]) -> list[T]:
    """Copy only the outer list in O(n) time and space."""
    return values.copy()


def nested_copy(values: list[list[T]]) -> list[list[T]]:
    """Recursively copy nested values in O(n) time and space."""
    return deepcopy(values)


def shared_rows(rows: int, columns: int, value: T) -> list[list[T]]:
    """Demonstrate the shared-row trap in O(rows + columns) time and space."""
    return [[value] * columns] * rows


def independent_rows(rows: int, columns: int, value: T) -> list[list[T]]:
    """Build distinct rows in O(rows * columns) time and space."""
    return [[value for _ in range(columns)] for _ in range(rows)]


def append_with_sentinel(value: T, values: list[T] | None = None) -> list[T]:
    """Append without sharing a mutable default; O(n) only when input is copied."""
    result = [] if values is None else values.copy()
    result.append(value)
    return result


def doubled(values: list[int]) -> list[int]:
    """Return doubled values without mutation in O(n) time and space."""
    return [value * 2 for value in values]


def double_in_place(values: list[int]) -> None:
    """Double the input in O(n) time and O(1) auxiliary space."""
    for index, value in enumerate(values):
        values[index] = value * 2
