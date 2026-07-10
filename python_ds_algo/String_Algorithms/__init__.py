"""String-search algorithms."""

from .kmp import build_lps, kmp_find_all, kmp_search

__all__ = ["build_lps", "kmp_find_all", "kmp_search"]
