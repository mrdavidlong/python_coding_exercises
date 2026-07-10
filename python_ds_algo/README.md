# Python DS & Algo

Data structures and algorithm implementations in Python, organized by topic.

See [ROADMAP.md](ROADMAP.md) for planned Python fundamentals and additional
data structures that do not duplicate the local `coding-interview-patterns`
exercise catalog.

## Structure

```
Graphs/          BFS, DFS, Dijkstra, topological sort, cycle detection, MST, Union-Find
Arrays/          Dynamic array implementing MutableSequence
Hash_Tables/     Chaining and linear-probing MutableMapping implementations
Heaps/           Min-heap (array + tree), heapify, heapsort
Intervals/       Interval data structure and operations
Sort and Search/ Bubble, merge, quick, counting, radix, bucket, insertion, selection sort
Stacks/          Stack and queue implementations
Trees/           Binary search tree operations
```

## Running tests

Requires Python 3.10 or newer. Create a fresh virtual environment and install
the development dependency from this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

```bash
# Run all tests
pytest

# Run tests for a specific topic
pytest Graphs/
pytest Trees/
pytest "Sort and Search/"

# Run a single test file
pytest Graphs/test_graphs.py

# Verbose output
pytest -v
```

The same suite can also be run from the parent repository with
`pytest python_ds_algo`. Run `bash run_all_tests.sh` there to test both
exercise projects.
