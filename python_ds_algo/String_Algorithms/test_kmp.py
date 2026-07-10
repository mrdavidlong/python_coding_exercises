import pytest

from String_Algorithms.kmp import build_lps, kmp_find_all, kmp_search


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [("", []), ("a", [0]), ("aaaa", [0, 1, 2, 3]), ("ababaca", [0, 0, 1, 2, 3, 0, 1])],
)
def test_lps_table(pattern: str, expected: list[int]) -> None:
    assert build_lps(pattern) == expected


@pytest.mark.parametrize(
    ("text", "pattern", "expected"),
    [("anything", "", 0), ("abc", "z", -1), ("abc", "b", 1),
     ("abxabcabcaby", "abcaby", 6), ("naïve café", "café", 6)],
)
def test_first_search(text: str, pattern: str, expected: int) -> None:
    assert kmp_search(text, pattern) == expected


def test_overlapping_and_repeated_prefix_matches() -> None:
    assert kmp_find_all("aaaa", "aa") == [0, 1, 2]
    assert kmp_find_all("ababab", "abab") == [0, 2]


def test_empty_pattern_matches_boundaries() -> None:
    assert kmp_find_all("abc", "") == [0, 1, 2, 3]
