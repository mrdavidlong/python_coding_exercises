from collections import deque
import heapq


class GraphNode:
    def __init__(self, val):
        self.val = val
        self.neighbors = []


class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self.adj = {}  # val -> list of (neighbor_val, weight)

    def add_node(self, val):
        if val not in self.adj:
            self.adj[val] = []

    def add_edge(self, u, v, weight=1):
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append((v, weight))
        if not self.directed:
            self.adj[v].append((u, weight))

    # --- Traversals ---

    def bfs(self, start):
        visited = set()
        order = []
        queue = deque([start])
        visited.add(start)
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor, _ in self.adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def dfs(self, start):
        visited = set()
        order = []
        self._dfs_recursive(start, visited, order)
        return order

    def _dfs_recursive(self, node, visited, order):
        visited.add(node)
        order.append(node)
        for neighbor, _ in self.adj.get(node, []):
            if neighbor not in visited:
                self._dfs_recursive(neighbor, visited, order)

    def dfs_iterative(self, start):
        visited = set()
        order = []
        stack = [start]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            order.append(node)
            for neighbor, _ in reversed(self.adj.get(node, [])):
                if neighbor not in visited:
                    stack.append(neighbor)
        return order

    # --- Shortest Path ---

    def dijkstra(self, start):
        dist = {node: float('inf') for node in self.adj}
        dist[start] = 0
        heap = [(0, start)]
        while heap:
            d, node = heapq.heappop(heap)
            if d > dist[node]:
                continue
            for neighbor, weight in self.adj.get(node, []):
                new_dist = d + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    heapq.heappush(heap, (new_dist, neighbor))
        return dist

    def bellman_ford(self, start):
        dist = {node: float('inf') for node in self.adj}
        dist[start] = 0
        edges = [(u, v, w) for u in self.adj for v, w in self.adj[u]]
        for _ in range(len(self.adj) - 1):
            for u, v, w in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                raise ValueError("Negative weight cycle detected")
        return dist

    # --- Connectivity ---

    def connected_components(self):
        visited = set()
        components = []
        for node in self.adj:
            if node not in visited:
                component = self.bfs(node)
                visited.update(component)
                components.append(component)
        return components

    def has_cycle_undirected(self):
        visited = set()

        def dfs(node, parent):
            visited.add(node)
            for neighbor, _ in self.adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, node):
                        return True
                elif neighbor != parent:
                    return True
            return False

        for node in self.adj:
            if node not in visited:
                if dfs(node, None):
                    return True
        return False

    def has_cycle_directed(self):
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor, _ in self.adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in self.adj:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def topological_sort(self):
        if not self.directed:
            raise ValueError("Topological sort requires a directed graph")
        visited = set()
        stack = []

        def dfs(node):
            visited.add(node)
            for neighbor, _ in self.adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
            stack.append(node)

        for node in self.adj:
            if node not in visited:
                dfs(node)
        return stack[::-1]

    def is_bipartite(self):
        color = {}
        for start in self.adj:
            if start in color:
                continue
            queue = deque([start])
            color[start] = 0
            while queue:
                node = queue.popleft()
                for neighbor, _ in self.adj.get(node, []):
                    if neighbor not in color:
                        color[neighbor] = 1 - color[node]
                        queue.append(neighbor)
                    elif color[neighbor] == color[node]:
                        return False
        return True

    # --- Minimum Spanning Tree ---

    def kruskal_mst(self):
        edges = sorted(
            [(w, u, v) for u in self.adj for v, w in self.adj[u]],
            key=lambda x: x[0]
        )
        uf = UnionFind(list(self.adj.keys()))
        mst = []
        for w, u, v in edges:
            if uf.find(u) != uf.find(v):
                uf.union(u, v)
                mst.append((u, v, w))
        return mst

    def prim_mst(self):
        if not self.adj:
            return []
        start = next(iter(self.adj))
        visited = set([start])
        heap = [(w, start, v) for v, w in self.adj[start]]
        heapq.heapify(heap)
        mst = []
        while heap:
            w, u, v = heapq.heappop(heap)
            if v in visited:
                continue
            visited.add(v)
            mst.append((u, v, w))
            for neighbor, weight in self.adj[v]:
                if neighbor not in visited:
                    heapq.heappush(heap, (weight, v, neighbor))
        return mst


# --- Union-Find / Disjoint Set ---

class UnionFind:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank = {n: 0 for n in nodes}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)
