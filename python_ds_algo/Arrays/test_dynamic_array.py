import pytest

from Arrays.dynamic_array import DynamicArray


def test_grows_and_preserves_order() -> None:
    values = DynamicArray(range(9), initial_capacity=2)
    assert list(values) == list(range(9))
    assert values.capacity >= len(values)


@pytest.mark.parametrize(
    ("index", "expected"),
    [(0, ["x", "a", "b"]), (1, ["a", "x", "b"]), (2, ["a", "b", "x"]),
     (-20, ["x", "a", "b"]), (20, ["a", "b", "x"])],
)
def test_insert_boundaries(index: int, expected: list[str]) -> None:
    values = DynamicArray(["a", "b"])
    values.insert(index, "x")
    assert list(values) == expected


def test_negative_access_assignment_and_deletion() -> None:
    values = DynamicArray([1, "two", 3.0])
    assert values[-1] == 3.0
    values[-2] = 2
    del values[-1]
    assert list(values) == [1, 2]


@pytest.mark.parametrize("operation", [lambda a: a[0], lambda a: a[-1], lambda a: a.__delitem__(0)])
def test_empty_indexes_raise(operation) -> None:
    with pytest.raises(IndexError):
        operation(DynamicArray())


def test_invalid_capacity_and_index_types() -> None:
    with pytest.raises(ValueError):
        DynamicArray(initial_capacity=0)
    with pytest.raises(TypeError):
        DynamicArray(initial_capacity=1.5)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        DynamicArray([1])["0"]  # type: ignore[index]


def test_slice_returns_independent_list() -> None:
    values = DynamicArray([0, 1, 2, 3])
    result = values[1:3]
    result.append(99)
    assert result == [1, 2, 99]
    assert list(values) == [0, 1, 2, 3]
