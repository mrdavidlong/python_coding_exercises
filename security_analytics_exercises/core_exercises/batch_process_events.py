"""
Problem: Process a potentially large list of security events in configurable
batches to avoid memory pressure. Yield each processed batch as a list.

The processor function is passed in as a callable — this pattern lets the
batch harness be reused with different processing logic.

Example:
    events = [{"id": i, "ts": i * 10} for i in range(100)]
    processor = lambda batch: [{"id": e["id"], "flagged": e["ts"] > 500} for e in batch]

    results = list(batch_process_events(events, processor, batch_size=10))
    # results is a list of 10 processed batches, each with 10 events
"""

from collections.abc import Callable, Generator
from typing import Any


def batch_process_events(
    events: list[dict[str, Any]],
    processor: Callable[[list[dict]], list[Any]],
    batch_size: int = 100,
) -> Generator[list[Any], None, None]:
    """Lazily yield processed results for each batch of events.

    Why a generator (yield) instead of returning a list of lists?
      Generators are lazy — the caller controls consumption speed.
      Good for back-pressure: DB writes, API calls, or retries between batches.

    Why accept a `processor` callable?
      Dependency injection: the chunking logic is reusable for any function
      (enrich, classify, write to DB…) without copy-pasting.

    Args:
        events:     Full list of event dicts to process.
                    e.g. [{"id":"e1",...}, {"id":"e2",...}, ...]  (can be thousands)
        processor:  Callable that takes a list of dicts and returns a list of results.
                    e.g. lambda batch: [enrich(e) for e in batch]
        batch_size: Number of events per batch.  e.g. 100

    Yields:
        One list of processed results per batch.
        e.g. for a 250-event input with batch_size=100:
             yields [results_0..99], [results_100..199], [results_200..249]
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    for start in range(0, len(events), batch_size):
        batch = events[start : start + batch_size]   # last batch may be smaller
        yield processor(batch)


def collect_all(
    events: list[dict[str, Any]],
    processor: Callable[[list[dict]], list[Any]],
    batch_size: int = 100,
) -> list[Any]:
    """Eagerly run all batches and return a single flat result list.

    Use this when you need all results at once (tests, small datasets).
    For large datasets where back-pressure matters, use batch_process_events directly.

    Args:
        events, processor, batch_size: same as batch_process_events.

    Returns:
        All processed results in a single flat list (not a list of lists).
        e.g. [result_e1, result_e2, ..., result_e250]
    """
    # Nested list comprehension — reads left to right, outer loop first:
    #   "for each batch yielded by batch_process_events, for each item in that batch"
    # The result is a flat list, not a list of lists.
    #
    # Equivalent multi-line version:
    #   result = []
    #   for batch in batch_process_events(events, processor, batch_size):
    #       for item in batch:
    #           result.append(item)
    #   return result
    return [item for batch in batch_process_events(events, processor, batch_size) for item in batch]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

EVENTS = [{"id": i, "ts": i * 10} for i in range(25)]
IDENTITY = lambda batch: batch  # processor that returns events unchanged


def test_correct_number_of_batches():
    batches = list(batch_process_events(EVENTS, IDENTITY, batch_size=10))
    # 25 events / 10 per batch = 3 batches (10, 10, 5)
    assert len(batches) == 3


def test_batch_sizes():
    batches = list(batch_process_events(EVENTS, IDENTITY, batch_size=10))
    assert len(batches[0]) == 10
    assert len(batches[1]) == 10
    assert len(batches[2]) == 5  # remainder


def test_processor_applied_to_each_batch():
    double_id = lambda batch: [{"id": e["id"] * 2} for e in batch]
    batches   = list(batch_process_events(EVENTS[:4], double_id, batch_size=2))
    assert batches[0][0]["id"] == 0
    assert batches[0][1]["id"] == 2


def test_collect_all_flattens():
    result = collect_all(EVENTS, IDENTITY, batch_size=10)
    assert len(result) == 25
    assert result[0]["id"] == 0
    assert result[-1]["id"] == 24


def test_empty_input():
    batches = list(batch_process_events([], IDENTITY, batch_size=10))
    assert batches == []


def test_batch_size_larger_than_input():
    batches = list(batch_process_events(EVENTS, IDENTITY, batch_size=1000))
    assert len(batches) == 1
    assert len(batches[0]) == 25


def test_invalid_batch_size_raises():
    try:
        list(batch_process_events(EVENTS, IDENTITY, batch_size=0))
        assert False, "Should have raised"
    except ValueError:
        pass


if __name__ == "__main__":
    test_correct_number_of_batches()
    test_batch_sizes()
    test_processor_applied_to_each_batch()
    test_collect_all_flattens()
    test_empty_input()
    test_batch_size_larger_than_input()
    test_invalid_batch_size_raises()
    print("All tests passed.")
