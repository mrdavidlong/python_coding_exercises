"""
Problem: Given a list of alert dicts, find the top N devices by alert count
within the last `window_hours` hours relative to a reference timestamp.

Example input:
    alerts = [
        {"device_id": "plc-01", "ts": 1700010000},
        {"device_id": "plc-01", "ts": 1700010100},
        {"device_id": "rtu-05", "ts": 1700010200},
        {"device_id": "plc-02", "ts": 1700010300},
        {"device_id": "plc-01", "ts": 1699900000},  # outside 24h window
    ]
    top_n_noisy_devices(alerts, n=2, window_hours=24, reference_ts=1700010400)

Expected output:
    [("plc-01", 2), ("rtu-05", 1)]   # plc-02 tied with rtu-05 but ordering by count desc then id
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def top_n_noisy_devices(
    alerts: list[dict[str, Any]],
    n: int,
    window_hours: int = 24,
    reference_ts: float | None = None,
) -> list[tuple[str, int]]:
    """Return the top N devices ranked by alert count within a time window.

    If reference_ts is None, the most recent alert timestamp is treated as "now".
    Ties in alert count are broken alphabetically by device_id for determinism.

    Args:
        alerts:       List of alert dicts, each with "device_id" (str) and "ts" (float).
                      e.g. [{"device_id":"plc-01","ts":1700010000},
                             {"device_id":"plc-01","ts":1700010100},
                             {"device_id":"rtu-05","ts":1700010200}]
        n:            Number of top devices to return.  e.g. 2
        window_hours: How far back to look from reference_ts.  e.g. 24
        reference_ts: Epoch seconds for "now". If None, uses max(ts) in alerts.
                      e.g. 1700010400

    Returns:
        List of (device_id, count) tuples, descending by count, alphabetical on ties.
        e.g. [("plc-01", 2), ("rtu-05", 1)]
    """
    if not alerts:
        return []

    # Determine the window start: "now" minus the window in seconds
    # Using max(ts) when reference_ts is absent means "relative to the latest alert"
    now    = reference_ts or max(a["ts"] for a in alerts)
    cutoff = now - window_hours * 3600   # anything before this is outside the window

    # Counter tallies device_ids in a single pass — equivalent to a GROUP BY COUNT(*)
    counts: Counter = Counter(
        a["device_id"] for a in alerts if a["ts"] >= cutoff
    )

    # Negate count so descending count sorts first in a normal ascending sort;
    # device_id as secondary key gives stable alphabetical tie-breaking
    # Alternative:
    #   import heapq                                                                                                                                                                                                  
    #   return heapq.nlargest(n, counts.items(), key=lambda x: (x[1], [-ord(c) for c in x[0]]))                                                                                                                                            
    # note:
    #   heapq.nlargest is O(d log n) vs sorted's O(d log d), where d = unique devices. Better when n << d.  
    # ⏺ - d = number of distinct device IDs (unique keys in counts)                                                                                                                                                   
    #   - n = the "top N" parameter passed to the function
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0])) #remember the tuple means first sort by desc and secondary sort by asc
    return ranked[:n]   # slice to the top N


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

REF_TS = 1700010400  # reference "now"
WINDOW = 24

SAMPLE_ALERTS = [
    {"device_id": "plc-01", "ts": 1700010000},
    {"device_id": "plc-01", "ts": 1700010100},
    {"device_id": "rtu-05", "ts": 1700010200},
    {"device_id": "plc-02", "ts": 1700010300},
    {"device_id": "plc-01", "ts": 1699900000},  # >24h ago — excluded
]


def test_top_2():
    result = top_n_noisy_devices(SAMPLE_ALERTS, n=2, window_hours=WINDOW, reference_ts=REF_TS)
    assert result[0] == ("plc-01", 2)
    assert len(result) == 2


def test_excludes_old_alerts():
    result = top_n_noisy_devices(SAMPLE_ALERTS, n=10, window_hours=WINDOW, reference_ts=REF_TS)
    total = sum(c for _, c in result)
    assert total == 4  # the old alert at 1699900000 is excluded


def test_empty_input():
    assert top_n_noisy_devices([], n=5) == []


def test_n_larger_than_devices():
    result = top_n_noisy_devices(SAMPLE_ALERTS, n=100, window_hours=WINDOW, reference_ts=REF_TS)
    assert len(result) == 3  # only 3 unique devices in window


def test_tie_breaking_is_deterministic():
    # rtu-05 and plc-02 each have 1 alert; plc-02 should come first alphabetically
    result = top_n_noisy_devices(SAMPLE_ALERTS, n=3, window_hours=WINDOW, reference_ts=REF_TS)
    device_ids = [d for d, _ in result]
    assert device_ids == ["plc-01", "plc-02", "rtu-05"]


if __name__ == "__main__":
    test_top_2()
    test_excludes_old_alerts()
    test_empty_input()
    test_n_larger_than_devices()
    test_tie_breaking_is_deterministic()
    print("All tests passed.")
