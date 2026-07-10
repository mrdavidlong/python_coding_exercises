"""Knuth-Morris-Pratt substring search."""


def build_lps(pattern: str) -> list[int]:
    """Build longest proper-prefix/suffix lengths in O(m) time and O(m) space."""
    lps = [0] * len(pattern)
    prefix_length = 0
    index = 1
    while index < len(pattern):
        if pattern[index] == pattern[prefix_length]:
            prefix_length += 1
            lps[index] = prefix_length
            index += 1
        elif prefix_length:
            prefix_length = lps[prefix_length - 1]
        else:
            index += 1
    return lps


def kmp_search(text: str, pattern: str) -> int:
    """Return the first match or -1 in O(n + m) time and O(m) space.

    Like ``str.find``, an empty pattern matches at index zero.
    """
    if not pattern:
        return 0
    lps = build_lps(pattern)
    matched = 0
    for index, character in enumerate(text):
        while matched and character != pattern[matched]:
            matched = lps[matched - 1]
        if character == pattern[matched]:
            matched += 1
            if matched == len(pattern):
                return index - len(pattern) + 1
    return -1


def kmp_find_all(text: str, pattern: str) -> list[int]:
    """Return all starts, including overlaps, in O(n + m) time and O(m + k) space.

    An empty pattern matches at every boundary, consistent with Python's
    substring-counting boundary model.
    """
    if not pattern:
        return list(range(len(text) + 1))
    lps = build_lps(pattern)
    matches: list[int] = []
    matched = 0
    for index, character in enumerate(text):
        while matched and character != pattern[matched]:
            matched = lps[matched - 1]
        if character == pattern[matched]:
            matched += 1
            if matched == len(pattern):
                matches.append(index - len(pattern) + 1)
                matched = lps[matched - 1]
    return matches
