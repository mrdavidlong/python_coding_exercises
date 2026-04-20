# Python DS & Algo

Data structures and algorithm implementations in Python, organized by topic.

## Structure

```
Graphs/          BFS, DFS, Dijkstra, topological sort, cycle detection, MST, Union-Find
Heaps/           Min-heap (array + tree), heapify, heapsort
Intervals/       Interval data structure and operations
Sort and Search/ Bubble, merge, quick, counting, radix, bucket, insertion, selection sort
Stacks/          Stack and queue implementations
Trees/           Binary search tree operations
```

## Running tests

Requires Python 3 and pytest.

```bash
# Run all tests
pytest

# Run tests for a specific topic
pytest Graphs/
pytest Trees/
pytest "Sort and Search/"

# Run a single test file
pytest Graphs/graphs_test.py

# Verbose output
pytest -v
```
