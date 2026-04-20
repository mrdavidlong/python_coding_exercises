import pytest
from graph import Graph, UnionFind


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_undirected():
    g = Graph(directed=False)
    for u, v in [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]:
        g.add_edge(u, v)
    return g


def make_directed():
    g = Graph(directed=True)
    for u, v in [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]:
        g.add_edge(u, v)
    return g


def make_weighted():
    g = Graph(directed=True)
    g.add_edge('A', 'B', 1)
    g.add_edge('A', 'C', 4)
    g.add_edge('B', 'C', 2)
    g.add_edge('B', 'D', 5)
    g.add_edge('C', 'D', 1)
    return g


# ---------------------------------------------------------------------------
# BFS
# ---------------------------------------------------------------------------

def test_bfs_visits_all_nodes():
    g = make_undirected()
    result = g.bfs(1)
    assert sorted(result) == [1, 2, 3, 4, 5]

def test_bfs_order():
    g = make_undirected()
    result = g.bfs(1)
    assert result[0] == 1
    assert set(result[1:3]) == {2, 3}

def test_bfs_disconnected():
    g = Graph(directed=False)
    g.add_edge(1, 2)
    g.add_edge(3, 4)
    assert sorted(g.bfs(1)) == [1, 2]
    assert sorted(g.bfs(3)) == [3, 4]


# ---------------------------------------------------------------------------
# DFS
# ---------------------------------------------------------------------------

def test_dfs_visits_all_nodes():
    g = make_undirected()
    assert sorted(g.dfs(1)) == [1, 2, 3, 4, 5]

def test_dfs_iterative_visits_all_nodes():
    g = make_undirected()
    assert sorted(g.dfs_iterative(1)) == [1, 2, 3, 4, 5]

def test_dfs_starts_at_root():
    g = make_undirected()
    assert g.dfs(1)[0] == 1
    assert g.dfs_iterative(1)[0] == 1


# ---------------------------------------------------------------------------
# Dijkstra
# ---------------------------------------------------------------------------

def test_dijkstra_distances():
    g = make_weighted()
    dist = g.dijkstra('A')
    assert dist['A'] == 0
    assert dist['B'] == 1
    assert dist['C'] == 3
    assert dist['D'] == 4

def test_dijkstra_unreachable():
    g = make_weighted()
    g.add_node('Z')
    dist = g.dijkstra('A')
    assert dist['Z'] == float('inf')


# ---------------------------------------------------------------------------
# Bellman-Ford
# ---------------------------------------------------------------------------

def test_bellman_ford_distances():
    g = make_weighted()
    dist = g.bellman_ford('A')
    assert dist['A'] == 0
    assert dist['B'] == 1
    assert dist['C'] == 3
    assert dist['D'] == 4

def test_bellman_ford_negative_cycle():
    g = Graph(directed=True)
    g.add_edge('A', 'B', 1)
    g.add_edge('B', 'C', -3)
    g.add_edge('C', 'A', 1)
    with pytest.raises(ValueError, match="Negative weight cycle"):
        g.bellman_ford('A')


# ---------------------------------------------------------------------------
# Connected Components
# ---------------------------------------------------------------------------

def test_connected_components_single():
    g = make_undirected()
    components = g.connected_components()
    assert len(components) == 1
    assert sorted(components[0]) == [1, 2, 3, 4, 5]

def test_connected_components_multiple():
    g = Graph(directed=False)
    g.add_edge(1, 2)
    g.add_edge(3, 4)
    g.add_node(5)
    components = g.connected_components()
    assert len(components) == 3


# ---------------------------------------------------------------------------
# Cycle Detection
# ---------------------------------------------------------------------------

def test_no_cycle_undirected():
    g = Graph(directed=False)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    assert not g.has_cycle_undirected()

def test_cycle_undirected():
    g = make_undirected()
    assert g.has_cycle_undirected()

def test_no_cycle_directed():
    g = make_directed()
    assert not g.has_cycle_directed()

def test_cycle_directed():
    g = Graph(directed=True)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)
    assert g.has_cycle_directed()


# ---------------------------------------------------------------------------
# Topological Sort
# ---------------------------------------------------------------------------

def test_topological_sort_order():
    g = make_directed()
    order = g.topological_sort()
    pos = {v: i for i, v in enumerate(order)}
    assert pos[1] < pos[2]
    assert pos[1] < pos[3]
    assert pos[2] < pos[4]
    assert pos[4] < pos[5]

def test_topological_sort_undirected_raises():
    g = make_undirected()
    with pytest.raises(ValueError):
        g.topological_sort()


# ---------------------------------------------------------------------------
# Bipartite
# ---------------------------------------------------------------------------

def test_bipartite_even_cycle():
    g = Graph(directed=False)
    for u, v in [(1, 2), (2, 3), (3, 4), (4, 1)]:
        g.add_edge(u, v)
    assert g.is_bipartite()

def test_not_bipartite_odd_cycle():
    g = Graph(directed=False)
    for u, v in [(1, 2), (2, 3), (3, 1)]:
        g.add_edge(u, v)
    assert not g.is_bipartite()


# ---------------------------------------------------------------------------
# MST — Kruskal & Prim
# ---------------------------------------------------------------------------

def make_undirected_weighted():
    g = Graph(directed=False)
    g.add_edge('A', 'B', 1)
    g.add_edge('A', 'C', 3)
    g.add_edge('B', 'C', 2)
    g.add_edge('B', 'D', 4)
    g.add_edge('C', 'D', 1)
    return g

def mst_total_weight(mst):
    return sum(w for _, _, w in mst)

def test_kruskal_mst_weight():
    g = make_undirected_weighted()
    mst = g.kruskal_mst()
    assert mst_total_weight(mst) == 4  # edges: AB(1) + CD(1) + BC(2)

def test_prim_mst_weight():
    g = make_undirected_weighted()
    mst = g.prim_mst()
    assert mst_total_weight(mst) == 4

def test_kruskal_mst_edge_count():
    g = make_undirected_weighted()
    mst = g.kruskal_mst()
    assert len(mst) == len(g.adj) - 1


# ---------------------------------------------------------------------------
# Union-Find
# ---------------------------------------------------------------------------

def test_union_find_basic():
    uf = UnionFind([1, 2, 3, 4])
    assert not uf.connected(1, 2)
    uf.union(1, 2)
    assert uf.connected(1, 2)

def test_union_find_transitive():
    uf = UnionFind([1, 2, 3])
    uf.union(1, 2)
    uf.union(2, 3)
    assert uf.connected(1, 3)

def test_union_find_no_duplicate_union():
    uf = UnionFind([1, 2])
    assert uf.union(1, 2) is True
    assert uf.union(1, 2) is False

def test_union_find_path_compression():
    uf = UnionFind(range(10))
    for i in range(9):
        uf.union(i, i + 1)
    root = uf.find(0)
    for i in range(10):
        assert uf.find(i) == root
