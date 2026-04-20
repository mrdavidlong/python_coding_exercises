import pytest
from collections import deque
from deque_demo import bfs_path, tail, roundrobin, delete_nth


def test_bfs_path_simple_tree():
    graph = {'A': ['B', 'C'], 'B': ['D', 'E'], 'C': ['F'], 'D': [], 'E': [], 'F': []}
    assert bfs_path(graph, 'A') == ['A', 'B', 'C', 'D', 'E', 'F']


def test_bfs_path_single_node():
    assert bfs_path({'A': []}, 'A') == ['A']


def test_bfs_path_linear():
    graph = {'A': ['B'], 'B': ['C'], 'C': []}
    assert bfs_path(graph, 'A') == ['A', 'B', 'C']


def test_tail(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("\n".join(str(i) for i in range(20)))
    result = tail(str(f), n=5)
    assert list(result) == [f"{i}\n" for i in range(15, 19)] + ["19"]


def test_roundrobin_equal_length():
    assert list(roundrobin('AB', 'CD')) == ['A', 'C', 'B', 'D']


def test_roundrobin_unequal_length():
    assert list(roundrobin('ABC', 'D', 'EF')) == ['A', 'D', 'E', 'B', 'F', 'C']


def test_roundrobin_single():
    assert list(roundrobin('ABC')) == ['A', 'B', 'C']


def test_delete_nth():
    d = deque([1, 2, 3, 4, 5])
    delete_nth(d, 2)
    assert list(d) == [1, 2, 4, 5]


def test_delete_nth_first():
    d = deque([1, 2, 3])
    delete_nth(d, 0)
    assert list(d) == [2, 3]
