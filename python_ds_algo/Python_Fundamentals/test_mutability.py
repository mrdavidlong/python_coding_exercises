from Python_Fundamentals.mutability import (
    alias, append_with_sentinel, double_in_place, doubled, independent_rows,
    nested_copy, shallow_copy, shared_rows,
)


def test_alias_shallow_and_deep_identity() -> None:
    original = [[1]]
    same = alias(original)
    shallow = shallow_copy(original)
    deep = nested_copy(original)
    assert same is original
    assert shallow is not original and shallow[0] is original[0]
    assert deep == original and deep[0] is not original[0]


def test_shared_row_bug_and_solution() -> None:
    buggy = shared_rows(2, 2, 0)
    fixed = independent_rows(2, 2, 0)
    buggy[0][0] = fixed[0][0] = 1
    assert buggy == [[1, 0], [1, 0]]
    assert fixed == [[1, 0], [0, 0]]
    assert buggy[0] is buggy[1]
    assert fixed[0] is not fixed[1]


def test_none_sentinel_does_not_share_calls_or_mutate_argument() -> None:
    assert append_with_sentinel(1) == [1]
    assert append_with_sentinel(2) == [2]
    source = [1]
    assert append_with_sentinel(2, source) == [1, 2]
    assert source == [1]


def test_pure_and_in_place_versions() -> None:
    source = [1, 2]
    result = doubled(source)
    assert result == [2, 4] and result is not source and source == [1, 2]
    assert double_in_place(source) is None
    assert source == [2, 4]
