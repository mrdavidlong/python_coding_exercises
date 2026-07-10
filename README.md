# Python Coding Exercises

This repository is a collection of Python practice projects focused on data structures, algorithms, and security analytics.

## Projects

- `python_ds_algo/` contains data structure and algorithm implementations, grouped by topic.
- `security_analytics_exercises/` contains exercises for alert processing, event correlation, and related security analytics tasks.

## Getting Started

Each project is self-contained. The data-structures project declares its
development dependency in `python_ds_algo/pyproject.toml` and can be installed
with `python -m pip install -e 'python_ds_algo[dev]'` from the repository root.
From either project directory, run its tests with `pytest`.

From the repository root, run both test suites with:

```bash
bash run_all_tests.sh
```

Examples:

```bash
cd python_ds_algo
pytest
```

```bash
cd security_analytics_exercises
pytest
```

## Notes

- Most exercises are small, focused Python modules with matching tests.
- Some folders use spaces in their names, so remember to quote paths like `Sort and Search` when running commands from the shell.
