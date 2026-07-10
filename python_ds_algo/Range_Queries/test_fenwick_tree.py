import random

import pytest

from Range_Queries.fenwick_tree import FenwickTree


def test_empty_singleton_and_boundaries() -> None:
    empty = FenwickTree()
    assert len(empty) == 0
    with pytest.raises(IndexError):
        empty.prefix_sum(0)
    tree = FenwickTree([5])
    assert tree.prefix_sum(0) == tree.range_sum(0, 0) == 5
    tree.add(0, -2)
    assert tree.prefix_sum(0) == 3


def test_queries_and_updates_against_list_reference() -> None:
    rng = random.Random(42)
    values = [rng.randrange(-10, 11) for _ in range(30)]
    tree = FenwickTree(values)
    for _ in range(100):
        if rng.choice([True, False]):
            index, delta = rng.randrange(len(values)), rng.randrange(-5, 6)
            values[index] += delta
            tree.add(index, delta)
        else:
            start, end = sorted(rng.sample(range(len(values)), 2))
            assert tree.prefix_sum(end) == sum(values[: end + 1])
            assert tree.range_sum(start, end) == sum(values[start : end + 1])


@pytest.mark.parametrize("index", [-1, 3])
def test_invalid_indexes(index: int) -> None:
    tree = FenwickTree([1, 2, 3])
    with pytest.raises(IndexError):
        tree.add(index, 1)
    with pytest.raises(IndexError):
        tree.prefix_sum(index)


def test_invalid_types_and_reversed_range() -> None:
    tree = FenwickTree([1, 2])
    with pytest.raises(TypeError):
        tree.prefix_sum(1.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        tree.range_sum(1, 0)
