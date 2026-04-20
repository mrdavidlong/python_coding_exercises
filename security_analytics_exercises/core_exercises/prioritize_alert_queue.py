"""
Problem: Build an alert priority queue where analysts always pop the highest-severity
alert first. Within the same severity, the earliest (lowest ts) alert is popped first.

How a min-heap achieves "highest severity first":
---------------------------------------------------------------------------

  Python's heapq is a MIN-heap: the SMALLEST tuple is always at the root.

  We map severities to integers so that CRITICAL gets the LOWEST number:
    CRITICAL=0, HIGH=1, MEDIUM=2, LOW=3, INFO=4

  Each item pushed is a 4-tuple:  (severity_rank, ts, counter, alert_dict)

  The heap compares tuples lexicographically:
    1. severity_rank  — smaller = higher priority (CRITICAL=0 wins)
    2. ts             — smaller = earlier timestamp (popped first on tie)
    3. counter        — insertion order (tie-breaker when rank AND ts are equal)
    4. alert_dict     — never actually compared (counter prevents reaching here)

  Heap structure after pushing LOW@1000, CRITICAL@2000, HIGH@1500, CRITICAL@1000:

          (0, 1000, 3, CRITICAL@1000)   ← root (popped first)
         /                             \
  (0, 2000, 1, CRITICAL@2000)   (1, 1500, 2, HIGH@1500)
  /
  (3, 1000, 0, LOW@1000)

  pop sequence:  CRITICAL@1000 → CRITICAL@2000 → HIGH@1500 → LOW@1000

  Why include `counter`?
    Without it, two alerts with the same (rank, ts) would force Python to
    compare the alert dicts — dicts don't support < — raising a TypeError.

Severity order (highest first): CRITICAL > HIGH > MEDIUM > LOW > INFO

Example:
    queue = AlertPriorityQueue()
    queue.push({"id": "a1", "severity": "LOW",      "ts": 1000})
    queue.push({"id": "a2", "severity": "CRITICAL", "ts": 2000})
    queue.push({"id": "a3", "severity": "HIGH",     "ts": 1500})
    queue.push({"id": "a4", "severity": "CRITICAL", "ts": 1000})

    queue.pop() → a4  (CRITICAL, earlier ts)
    queue.pop() → a2  (CRITICAL, later ts)
    queue.pop() → a3  (HIGH)
    queue.pop() → a1  (LOW)
"""

import heapq
from typing import Any

# Map severity label → heap priority (lower number = popped first)
SEVERITY_PRIORITY: dict[str, int] = {
    "CRITICAL": 0,
    "HIGH":     1,
    "MEDIUM":   2,
    "LOW":      3,
    "INFO":     4,
}


class AlertPriorityQueue:
    """Min-heap based alert queue. Higher severity = popped first."""

    def __init__(self) -> None:
        # e.g. [(1, 0, {"severity":"CRITICAL",...}), (2, 1, {"severity":"HIGH",...})]
        #       ^priority ^counter ^alert_dict
        self._heap: list[tuple] = []
        # Monotonically increasing counter breaks ties when (severity, ts) collide,
        # ensuring Python never has to compare two alert dicts directly.
        self._counter = 0

    def push(self, alert: dict[str, Any]) -> None:
        """Add an alert to the queue."""
        rank = SEVERITY_PRIORITY.get(alert.get("severity", "INFO"), 4)
        # Pack into a tuple that heapq can compare without touching the dict
        heapq.heappush(self._heap, (rank, alert["ts"], self._counter, alert))
        self._counter += 1

    def pop(self) -> dict[str, Any]:
        """Remove and return the highest-priority (lowest rank) alert."""
        if not self._heap:
            raise IndexError("pop from empty alert queue")
        # Unpack and discard the bookkeeping fields; return only the alert dict
        _, _, _, alert = heapq.heappop(self._heap)
        return alert

    def peek(self) -> dict[str, Any]:
        """Return (but do not remove) the highest-priority alert."""
        if not self._heap:
            raise IndexError("peek at empty alert queue")
        return self._heap[0][3]   # root of heap is index 0; alert is at position 3

    def __len__(self) -> int:
        return len(self._heap)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_severity_ordering():
    q = AlertPriorityQueue()
    q.push({"id": "low",      "severity": "LOW",      "ts": 1000})
    q.push({"id": "critical", "severity": "CRITICAL", "ts": 2000})
    q.push({"id": "high",     "severity": "HIGH",     "ts": 1500})
    assert q.pop()["id"] == "critical"
    assert q.pop()["id"] == "high"
    assert q.pop()["id"] == "low"


def test_same_severity_earlier_ts_first():
    q = AlertPriorityQueue()
    q.push({"id": "a2", "severity": "CRITICAL", "ts": 2000})
    q.push({"id": "a1", "severity": "CRITICAL", "ts": 1000})
    assert q.pop()["id"] == "a1"   # ts=1000 < ts=2000 → popped first


def test_peek_does_not_remove():
    q = AlertPriorityQueue()
    q.push({"id": "x", "severity": "HIGH", "ts": 100})
    q.peek()
    assert len(q) == 1


def test_len():
    q = AlertPriorityQueue()
    assert len(q) == 0
    q.push({"id": "a", "severity": "LOW", "ts": 0})
    assert len(q) == 1


def test_pop_from_empty_raises():
    q = AlertPriorityQueue()
    try:
        q.pop()
        assert False, "Should have raised"
    except IndexError:
        pass


def test_unknown_severity_treated_as_info():
    q = AlertPriorityQueue()
    q.push({"id": "info", "severity": "INFO",    "ts": 1})
    q.push({"id": "unk",  "severity": "MYSTERY", "ts": 2})
    # Both get rank 4; info has earlier ts → popped first
    assert q.pop()["id"] == "info"


if __name__ == "__main__":
    test_severity_ordering()
    test_same_severity_earlier_ts_first()
    test_peek_does_not_remove()
    test_len()
    test_pop_from_empty_raises()
    test_unknown_severity_treated_as_info()
    print("All tests passed.")
