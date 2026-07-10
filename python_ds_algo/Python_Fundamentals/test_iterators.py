import pytest

from Python_Fundamentals.iterators import Countdown, Peekable, chunked, flatten


def test_custom_iterator_exhaustion_and_identity() -> None:
    countdown = Countdown(2)
    assert iter(countdown) is countdown
    assert list(countdown) == [2, 1]
    assert list(countdown) == []
    with pytest.raises(ValueError):
        Countdown(-1)


def test_peekable_does_not_advance_visible_item() -> None:
    values = Peekable(iter([1, 2]))
    assert values.peek() == values.peek() == 1
    assert next(values) == 1
    assert list(values) == [2]
    with pytest.raises(StopIteration):
        values.peek()


def test_chunked_is_lazy_and_validates_on_iteration() -> None:
    seen: list[int] = []
    source = (seen.append(n) or n for n in range(5))
    chunks = chunked(source, 2)
    assert seen == []
    assert next(chunks) == [0, 1] and seen == [0, 1]
    assert list(chunks) == [[2, 3], [4]]
    with pytest.raises(ValueError):
        next(chunked([], 0))


def test_recursive_flatten_and_strings() -> None:
    assert list(flatten([1, [2, (3, 4)], "five"])) == [1, 2, 3, 4, "five"]
