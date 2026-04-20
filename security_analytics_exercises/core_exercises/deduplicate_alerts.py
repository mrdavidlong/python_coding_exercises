"""
Problem: Given a list of alert dicts, remove duplicates where two alerts share
the same (device_id, alert_type) and fall within `window_seconds` of each other.
Keep the first occurrence of each duplicate cluster.

How time-window suppression works:
---------------------------------------------------------------------------

  key = ("plc-01", "auth_failure"),  window = 60s

  ts:    1000   1045   1200   1260
  alert: [a1]   [a2]   [a3]   [a4]

  Step 1 — a1 (ts=1000):
    last_seen[key] = None → EMIT,  last_seen[key] = 1000

  Step 2 — a2 (ts=1045):
    1045 - 1000 = 45s  → 45 ≤ 60  → SUPPRESS

  Step 3 — a3 (ts=1200):
    1200 - 1000 = 200s → 200 > 60 → EMIT,  last_seen[key] = 1200  (new cluster)

  Step 4 — a4 (ts=1260):
    1260 - 1200 = 60s  → 60 ≤ 60  → SUPPRESS  (must be strictly > 60s to pass)

  Output: [a1, a3]

Key insight: last_seen resets to the EMITTED alert's ts, not the window end.
So each emitted alert starts a fresh 60s suppression window.

Example input:
    alerts = [
        {"id": "a1", "device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000},
        {"id": "a2", "device_id": "plc-01", "alert_type": "auth_failure", "ts": 1045},  # dup of a1
        {"id": "a3", "device_id": "plc-01", "alert_type": "auth_failure", "ts": 1200},  # new cluster
        {"id": "a4", "device_id": "rtu-05", "alert_type": "auth_failure", "ts": 1000},  # diff device
    ]
    deduplicate_alerts(alerts, window_seconds=60)

Expected output:  [a1, a3, a4]
"""

from typing import Any


def deduplicate_alerts(
    alerts: list[dict[str, Any]],
    window_seconds: int = 60,
) -> list[dict[str, Any]]:
    """Suppress repeat alerts for the same (device_id, alert_type) within a cooldown window.

    Each emitted alert resets the cooldown clock for its key. Alerts are
    processed in timestamp order; the output is also sorted by ts.

    Args:
        alerts:         List of alert dicts, each with "device_id", "alert_type", "ts".
                        e.g. [{"device_id":"plc-01","alert_type":"auth_failure","ts":1000},
                               {"device_id":"plc-01","alert_type":"auth_failure","ts":1045},
                               {"device_id":"plc-01","alert_type":"auth_failure","ts":1200}]
        window_seconds: Cooldown in seconds. An alert is suppressed if its gap
                        from the last emitted alert is <= this value.  e.g. 60

    Returns:
        Deduplicated list sorted by ts.
        e.g. [ts=1000 (emitted), ts=1200 (emitted, 200s gap > 60)]
             ts=1045 is dropped (45s gap ≤ 60)
    """
    # Plain dict (not defaultdict): a missing key signals "never seen before",
    # which .get(key) returns as None — the None check IS the logic on line below.
    # defaultdict(float) would silently return 0.0, making it look like a real ts.
    # e.g. {("plc-01", "auth_failure"): 1000.0, ("rtu-05", "scan"): 1200.0}
    last_seen: dict[tuple[str, str], float] = {}
    result = []

    # Sort first so we always compare an alert against the earliest prior match,
    # not an arbitrary order from the input.
    for alert in sorted(alerts, key=lambda a: a["ts"]):
        key     = (alert["device_id"], alert["alert_type"])
        prev_ts = last_seen.get(key)

        # Emit if: (a) we've never seen this key, OR
        #          (b) gap since last emit is strictly greater than the window.
        # Using strict > means an alert at exactly window_seconds is still suppressed.
        if prev_ts is None or (alert["ts"] - prev_ts) > window_seconds:
            result.append(alert)
            last_seen[key] = alert["ts"]   # anchor the new suppression window here

    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SAMPLE_ALERTS = [
    {"id": "a1", "device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000},
    {"id": "a2", "device_id": "plc-01", "alert_type": "auth_failure", "ts": 1045},  # dup
    {"id": "a3", "device_id": "plc-01", "alert_type": "auth_failure", "ts": 1200},  # new cluster
    {"id": "a4", "device_id": "rtu-05", "alert_type": "auth_failure", "ts": 1000},  # diff device
    {"id": "a5", "device_id": "plc-01", "alert_type": "cmd_inject",   "ts": 1001},  # diff type
]


def test_basic_dedup():
    result = deduplicate_alerts(SAMPLE_ALERTS, window_seconds=60)
    ids = {a["id"] for a in result}
    assert "a1" in ids
    assert "a2" not in ids  # suppressed — within 60s of a1
    assert "a3" in ids      # 200s after a1 — new cluster
    assert "a4" in ids      # different device key
    assert "a5" in ids      # different alert_type key


def test_no_duplicates():
    alerts = [
        {"id": "x1", "device_id": "d1", "alert_type": "t1", "ts": 0},
        {"id": "x2", "device_id": "d2", "alert_type": "t1", "ts": 1},
    ]
    result = deduplicate_alerts(alerts, window_seconds=60)
    assert len(result) == 2


def test_all_duplicates():
    alerts = [
        {"id": f"a{i}", "device_id": "d1", "alert_type": "t1", "ts": i * 10}
        for i in range(5)  # ts: 0, 10, 20, 30, 40 — all within 60s of first
    ]
    result = deduplicate_alerts(alerts, window_seconds=60)
    assert len(result) == 1
    assert result[0]["id"] == "a0"


def test_empty_input():
    assert deduplicate_alerts([]) == []


def test_exact_boundary():
    alerts = [
        {"id": "b1", "device_id": "d1", "alert_type": "t1", "ts": 0},
        {"id": "b2", "device_id": "d1", "alert_type": "t1", "ts": 60},   # exactly at window edge
        {"id": "b3", "device_id": "d1", "alert_type": "t1", "ts": 61},   # just outside
    ]
    result = deduplicate_alerts(alerts, window_seconds=60)
    ids = [a["id"] for a in result]
    # ts=60 → gap=60, NOT > 60 → still suppressed
    # ts=61 → gap=61, > 60 → emitted
    assert ids == ["b1", "b3"]


if __name__ == "__main__":
    test_basic_dedup()
    test_no_duplicates()
    test_all_duplicates()
    test_empty_input()
    test_exact_boundary()
    print("All tests passed.")
