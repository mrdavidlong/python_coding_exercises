import pytest

from Python_Fundamentals.iteration_patterns import (
    boundary_truth, indexed_pairs, pairwise_totals, sort_in_place,
    squares_by_parity, stable_rank, transpose, unique_lengths,
)


def test_enumerate_zip_and_unpacking() -> None:
    assert indexed_pairs("ab") == [(0, "a"), (1, "b")]
    assert pairwise_totals([1, 2, 99], [10, 20]) == [11, 22]


def test_comprehensions_and_transpose() -> None:
    assert unique_lengths(["a", "to", "be"]) == {1, 2}
    assert squares_by_parity(range(4)) == {"even": [0, 4], "odd": [1, 9]}
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert transpose([]) == []
    with pytest.raises(ValueError):
        transpose([[1], [2, 3]])


def test_any_all_empty_boundaries() -> None:
    assert boundary_truth([]) == (False, True)
    assert boundary_truth([True, False]) == (True, False)


def test_sorting_semantics_and_ties() -> None:
    records = [("zoe", 2), ("amy", 2), ("bob", 1)]
    ranked = stable_rank(records)
    assert ranked == [("amy", 2), ("zoe", 2), ("bob", 1)]
    assert records == [("zoe", 2), ("amy", 2), ("bob", 1)]
    values = [2, 1]
    assert sort_in_place(values) is None
    assert values == [1, 2]
