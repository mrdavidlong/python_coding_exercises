import itertools
from collections import deque

# deque (double-ended queue) supports O(1) appends and pops from both ends,
# unlike list which is O(n) for popleft/insert(0, ...).

def bfs_path(graph, start):
    # BFS uses a queue so nodes are visited in order of increasing distance from start.
    order = []
    queue = deque([start])
    visited = {start}

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

# Test BFS on a simple tree-like graph
# graph = {'A': ['B', 'C'], 'B': ['D', 'E'], 'C': ['F'], 'D': [], 'E': [], 'F': []}
# path = bfs_path(graph, 'A')
# print(f"BFS Traversal Order starting from A: {' -> '.join(path)}")


# https://docs.python.org/3/library/collections.html#deque-recipes
def tail(filename, n=10):
    # deque with maxlen discards from the left as new lines are appended,
    # so only the last n lines are kept — no need to read the whole file into memory.
    with open(filename) as f:
        return deque(f, n)


def moving_average(iterable, n=3):
    # moving_average([40, 30, 50, 46, 39, 44]) --> 40.0 42.0 45.0 43.0
    # https://en.wikipedia.org/wiki/Moving_average
    it = iter(iterable)
    d = deque(itertools.islice(it, n-1))
    d.appendleft(0)          # pad so the window is full-width from the first yield
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        yield s / n



def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # rotate(-1) moves the front iterator to the back after each yield,
    # cycling through all active iterators evenly.
    iterators = deque(map(iter, iterables))
    while iterators:
        try:
            while True:
                yield next(iterators[0])
                iterators.rotate(-1)
        except StopIteration:
            # Remove an exhausted iterator.
            iterators.popleft()


def delete_nth(d, n):
    # rotate brings the target element to the front, remove it, then restore original order.
    d.rotate(-n)
    d.popleft()
    d.rotate(n)