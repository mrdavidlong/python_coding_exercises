"""
Problem: Given two event streams (from different devices or sensors), find pairs
of events that occur within `max_delta_seconds` of each other.

How binary-search correlation works:
---------------------------------------------------------------------------

  stream_b sorted by ts: [b1@100, b2@500, b3@1500]
                           idx=0   idx=1   idx=2

  For event_a with ts=105, max_delta=10:

    bisect_left(b_timestamps, 105) returns idx=1
    (idx=1 is the first position where 105 could be inserted to keep order)

    Candidates to check: idx-1=0 and idx=1

      idx=0: b1@100  → |105-100| = 5  ≤ 10  ✓  delta=5
      idx=1: b2@500  → |105-500| = 395 > 10  ✗

    Best match: b1 (delta=5) → pair (a, b1)

  Why only check idx-1 and idx?
    The sorted list means the nearest element is always immediately
    to the left or right of the bisect insertion point. Anything further
    away is guaranteed to have a larger delta.

  Greedy one-to-one matching:
    Once b1 is matched, it's added to matched_b_idxs and skipped for
    future a-events. This prevents "double counting" a b-event.

Example input:
    stream_a = [{"id": "a1", "ts": 1000}, {"id": "a2", "ts": 2000}]
    stream_b = [{"id": "b1", "ts": 1005}, {"id": "b2", "ts": 3000}]
    max_delta_seconds = 10

Expected output:  [( {"id": "a1", ...}, {"id": "b1", ...} )]
                  a2 and b2 are 1000s apart — no match
"""

from typing import Any
import bisect


def correlate_streams(
    stream_a: list[dict[str, Any]],
    stream_b: list[dict[str, Any]],
    max_delta_seconds: float = 5.0,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Pair events from two streams that occur within max_delta_seconds of each other.

    Algorithm: O(n log m) — sort stream_b once, binary-search per a-event.
    Each stream_b event is matched at most once (greedy first-match, no reuse).

    Args:
        stream_a:           First event stream. Each dict must have "ts" (float).
                            e.g. [{"id":"a1","device_id":"plc-01","ts":1000.0}]
        stream_b:           Second event stream, same format.
                            e.g. [{"id":"b1","device_id":"rtu-05","ts":1002.0}]
        max_delta_seconds:  Maximum time gap (seconds) for a pair to be considered
                            correlated. Inclusive comparison (|ts_a - ts_b| ≤ delta).
                            e.g. 5.0

    Returns:
        List of (event_a, event_b) tuples where the events are within delta of each other.
        e.g. [({"id":"a1","ts":1000.0}, {"id":"b1","ts":1002.0})]
        No event from either stream appears in more than one pair.
    """
    if not stream_a or not stream_b:
        return []

    # Pre-sort stream_b and extract timestamps for binary search
    sorted_b     = sorted(stream_b, key=lambda e: e["ts"])
    b_timestamps = [e["ts"] for e in sorted_b]  # parallel list for bisect

    # Track which stream_b indices have already been matched to avoid reuse
    # e.g. {2, 5} means sorted_b[2] and sorted_b[5] are already paired
    matched_b_idxs: set[int] = set()

    pairs = []
    for event_a in sorted(stream_a, key=lambda e: e["ts"]):
        ts_a = event_a["ts"]

        # bisect_left returns the index where ts_a would be inserted to keep
        # b_timestamps sorted. The nearest b-event is at idx or idx-1.
        idx = bisect.bisect_left(b_timestamps, ts_a)

        best_idx   = None
        best_delta = float("inf")

        # Check the candidate immediately to the left (idx-1) and to the right (idx)
        for candidate_idx in [idx - 1, idx]:
            if candidate_idx < 0 or candidate_idx >= len(sorted_b):
                continue  # out of bounds
            if candidate_idx in matched_b_idxs:
                continue  # already consumed by an earlier a-event

            delta = abs(sorted_b[candidate_idx]["ts"] - ts_a)
            if delta <= max_delta_seconds and delta < best_delta:
                best_delta = delta
                best_idx   = candidate_idx

        if best_idx is not None:
            matched_b_idxs.add(best_idx)                        # mark consumed
            pairs.append((event_a, sorted_b[best_idx]))

    return pairs


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

STREAM_A = [{"id": "a1", "ts": 1000}, {"id": "a2", "ts": 2000}]
STREAM_B = [{"id": "b1", "ts": 1005}, {"id": "b2", "ts": 3000}]


def test_basic_correlation():
    result = correlate_streams(STREAM_A, STREAM_B, max_delta_seconds=10)
    assert len(result) == 1
    a, b = result[0]
    assert a["id"] == "a1" and b["id"] == "b1"


def test_no_match_when_too_far_apart():
    result = correlate_streams(STREAM_A, STREAM_B, max_delta_seconds=1)
    assert result == []  # a1-b1 gap is 5s, threshold is 1s


def test_each_b_event_matched_at_most_once():
    # Both a-events are close to b1; only the first one should match
    a = [{"id": "a1", "ts": 100}, {"id": "a2", "ts": 102}]
    b = [{"id": "b1", "ts": 101}]
    result = correlate_streams(a, b, max_delta_seconds=10)
    assert len(result) == 1  # b1 consumed by a1; a2 finds nothing


def test_empty_streams():
    assert correlate_streams([], STREAM_B) == []
    assert correlate_streams(STREAM_A, []) == []


def test_exact_boundary_match():
    a = [{"id": "a1", "ts": 1000}]
    b = [{"id": "b1", "ts": 1005}]
    assert len(correlate_streams(a, b, max_delta_seconds=5)) == 1   # delta=5 ≤ 5
    assert len(correlate_streams(a, b, max_delta_seconds=4)) == 0   # delta=5 > 4


if __name__ == "__main__":
    test_basic_correlation()
    test_no_match_when_too_far_apart()
    test_each_b_event_matched_at_most_once()
    test_empty_streams()
    test_exact_boundary_match()
    print("All tests passed.")
