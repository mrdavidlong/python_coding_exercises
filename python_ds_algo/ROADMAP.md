# Python DSA and Fundamentals Roadmap

This roadmap expands the repository with Python concepts and data-structure
implementations that are useful in coding interviews without recreating the
exercise catalog in `coding-interview-patterns`.

## Scope and deduplication rule

Before adding an exercise, compare it with the Python implementations in the
local reference checkout:

```text
/Users/davidlong/code/interview/coding-interview-patterns/python3
```

The reference checkout is only a topic index. New implementations must be
written for this repository rather than copied from it.

Do not add another version of a problem already covered there unless the new
exercise has a clearly different learning objective documented in its module.
The following areas are already well represented and are therefore out of
scope for this roadmap:

- Backtracking
- Binary search
- Bit manipulation
- Dynamic programming
- Fast and slow pointers
- Graph interview problems and matrix traversal
- Greedy algorithms
- Hash-map and set problem patterns
- Heap interview problems
- Interval problem patterns
- Linked-list interview problems
- Math and geometry problems
- Prefix sums
- Sliding windows
- Sorting interview problems
- Stack problem patterns
- Tree interview problems
- Tries
- Two pointers

Implementing the internals of a data structure is not considered a duplicate
of solving problems with Python's built-in version of that structure. For
example, implementing collision handling in a hash table is in scope even
though the reference repository contains problems that use `dict` and `set`.

## General implementation standards

Every new topic should:

- Include focused implementation modules and matching pytest tests.
- State the relevant time and space complexity in docstrings.
- Use type hints where they improve clarity.
- Avoid executable demonstration code during import.
- Define and test whether an operation mutates its input.
- Cover empty, singleton, boundary, duplicate, and invalid inputs as relevant.
- Prefer parameterized tests when multiple implementations share a contract.
- Keep examples small enough to study during interview preparation.

## Phase 0: Test and package foundation

Status: complete

Deliverables:

- Add a project-level `pyproject.toml` with pytest configuration.
- Replace the stale local virtual environment rather than committing it.
- Make imports reliable when tests run from either this directory or the
  parent repository.
- Update the testing instructions in this README and the parent README.
- Confirm that the parent `run_all_tests.sh` runs both exercise projects.

Acceptance checks:

- A clean environment can install the development dependencies.
- `pytest` passes from `python_ds_algo/`.
- The shared test command passes from the parent repository.

## Phase 1: Dynamic array and the sequence protocol

Status: planned

Proposed files:

```text
Arrays/
    dynamic_array.py
    test_dynamic_array.py
```

Implement a generic `DynamicArray` that inherits from
`collections.abc.MutableSequence`. Override the abstract sequence methods:

- `__len__`
- `__getitem__`
- `__setitem__`
- `__delitem__`
- `insert`

Learning goals:

- Class inheritance and method overriding
- Python abstract base classes
- Collection dunder methods
- Negative indexing and bounds validation
- Capacity growth and amortized `O(1)` append
- The difference between logical length and allocated capacity

Tests should cover resizing, insertion at every boundary, deletion, negative
indexes, invalid indexes, iteration, mixed value types, and order preservation.

## Phase 2: Hash tables and polymorphic collision strategies

Status: planned

Proposed files:

```text
Hash_Tables/
    hash_table.py
    chained_hash_table.py
    linear_probing_hash_table.py
    test_hash_tables.py
```

Create a common mapping contract and two implementations:

```text
MutableMapping
└── HashTable
    ├── ChainedHashTable
    └── LinearProbingHashTable
```

The base class should own shared validation, capacity, load-factor, resizing,
and mapping behavior. Subclasses should override the collision-specific
lookup, insertion, deletion, and rehash hooks. Use `super()` where a subclass
extends shared initialization or resizing behavior.

Learning goals:

- Inheritance, abstract methods, overriding, and polymorphism
- The template-method pattern
- Python's mutable-mapping protocol
- Separate chaining versus open addressing
- Tombstones and probe sequences
- Load factors, resizing, and rehashing

Run the same parameterized contract tests against both implementations. Add
controlled-collision keys, deletion followed by lookup, update-without-growth,
resize, missing-key, and invalid-capacity cases.

## Phase 3: Mutability and copying

Status: planned

Proposed files:

```text
Python_Fundamentals/
    mutability.py
    test_mutability.py
```

Learning exercises should demonstrate:

- Aliasing versus copying
- Shallow versus nested copying
- The shared-row matrix initialization bug
- Mutable default-argument behavior and the `None` sentinel solution
- Pure functions versus in-place mutation
- Equality versus object identity

Tests should assert both values and identities so the behavior is explicit.

## Phase 4: Iteration, comprehensions, and sorting semantics

Status: planned

Proposed files:

```text
Python_Fundamentals/
    iteration_patterns.py
    test_iteration_patterns.py
```

Cover language tools rather than duplicating interview problems:

- `enumerate`, `zip`, and tuple unpacking
- List, set, and dictionary comprehensions
- Safe nested comprehensions and matrix transposition
- `any` and `all`
- `sorted()` versus `list.sort()`
- Stable sorting and compound keys
- Descending primary keys with deterministic ascending tie-breakers

Tests should verify result ordering, tie behavior, and whether the original
input was mutated.

## Phase 5: Iterators and generators

Status: planned

Proposed files:

```text
Python_Fundamentals/
    iterators.py
    test_iterators.py
```

Implement a small custom iterator, a peekable iterator, a lazy `chunked()`
generator, and recursive flattening with `yield from`.

Learning goals:

- `iter()`, `next()`, `__iter__`, and `__next__`
- `StopIteration`
- `yield` and `yield from`
- Lazy versus eager evaluation
- Generator exhaustion and single-use iterators

Do not add another algorithmic sliding-window exercise; that pattern is
already covered in the reference repository.

## Phase 6: Dataclasses and the Python object model

Status: planned

Proposed files:

```text
Python_Fundamentals/
    data_models.py
    test_data_models.py
```

Use small DSA-oriented value objects to demonstrate:

- `@dataclass`
- Equality and readable representations
- Frozen objects and hashability
- Ordering and heap tie-breaking
- `ClassVar`
- Instance, class, and static methods
- Carefully chosen custom dunder methods

This phase should teach language behavior without reimplementing interval or
heap problems from the reference repository.

## Phase 7: KMP string search

Status: planned

Proposed files:

```text
String_Algorithms/
    kmp.py
    test_kmp.py
```

Implement prefix/LPS table construction and Knuth-Morris-Pratt search. Test
empty patterns, missing patterns, repeated prefixes, overlapping matches,
single-character patterns, and Unicode text.

This algorithm was not present in the reviewed Python reference catalog.

## Phase 8: Fenwick tree

Status: optional

Proposed files:

```text
Range_Queries/
    fenwick_tree.py
    test_fenwick_tree.py
```

Implement construction, point updates, prefix sums, and range sums. Document
one-based internal indexing and the `index & -index` operation. Include tests
that compare operations with a simple list-based reference implementation.

This is lower priority than the Python fundamentals and core data structures.

## Recommended execution order

1. Test and package foundation
2. Dynamic array
3. Hash-table hierarchy
4. Mutability and copying
5. Iteration and sorting semantics
6. Iterators and generators
7. Dataclasses and the object model
8. KMP string search
9. Fenwick tree, if additional advanced material is wanted

Complete and test one phase before starting the next. Recheck the external
topic catalog at the start of each algorithm phase because it may change over
time.
