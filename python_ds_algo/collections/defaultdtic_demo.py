from collections import defaultdict

def build_graph(edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    return graph

# Test building a simple network
connections = [('Home', 'Router'), ('Router', 'Internet'), ('Router', 'Phone')]
network = build_graph(connections)

print("Nodes in network and their connections:")
for node, neighbors in network.items():
    print(f"{node} is connected to: {neighbors}")
