"""
Problem: Find devices that have had N or more anomaly events in a row with no
normal event in between. The event log contains events with status "ANOMALY"
or "NORMAL" per device.

How trailing-run detection works:
---------------------------------------------------------------------------

  We only care about the CURRENT state of a device — whether it is STILL in
  an anomaly run right now. A past anomaly that was followed by a NORMAL event
  is resolved and doesn't count.

  Strategy: scan each device's events in REVERSE (newest → oldest).
  Count consecutive ANOMALY events from the end. Stop at the first NORMAL.

  plc-01 event log (sorted by ts):
    ts=100  NORMAL   ←── historical, doesn't matter
    ts=200  ANOMALY
    ts=300  ANOMALY
    ts=400  ANOMALY  ← most recent

  Reverse scan:
    ts=400  ANOMALY  → run=1
    ts=300  ANOMALY  → run=2
    ts=200  ANOMALY  → run=3
    ts=100  NORMAL   → STOP  (trailing run = 3)

  rtu-05 event log:
    ts=100  ANOMALY
    ts=200  NORMAL   ← breaks the run
    ts=300  ANOMALY  ← most recent

  Reverse scan:
    ts=300  ANOMALY  → run=1
    ts=200  NORMAL   → STOP  (trailing run = 1)

  With min_run=3 → only plc-01 qualifies.

Return a list of devices currently in an anomaly run of >= min_run length,
along with the run length.

Example input:
    events = [
        {"device_id": "plc-01", "status": "NORMAL",  "ts": 100},
        {"device_id": "plc-01", "status": "ANOMALY", "ts": 200},
        {"device_id": "plc-01", "status": "ANOMALY", "ts": 300},
        {"device_id": "plc-01", "status": "ANOMALY", "ts": 400},
        {"device_id": "rtu-05", "status": "ANOMALY", "ts": 100},
        {"device_id": "rtu-05", "status": "NORMAL",  "ts": 200},  # resets run
        {"device_id": "rtu-05", "status": "ANOMALY", "ts": 300},
    ]
    detect_consecutive_anomalies(events, min_run=3)

Expected output:  [{"device_id": "plc-01", "run_length": 3}]
"""

from collections import defaultdict
from typing import Any


def detect_consecutive_anomalies(
    events: list[dict[str, Any]],
    min_run: int = 3,
) -> list[dict[str, Any]]:
    """Find devices whose most recent consecutive anomaly run is >= min_run.

    Only the TRAILING run matters: a device with 5 anomalies then 1 normal
    then 2 anomalies has a trailing run of 2, not 5.

    Args:
        events:  List of event dicts with "device_id" (str) and "type" (str).
                 Events are sorted by ts per device before analysis.
                 "anomaly" type counts toward the run; anything else breaks it.
                 e.g. [{"device_id":"plc-01","type":"anomaly","ts":1},
                        {"device_id":"plc-01","type":"anomaly","ts":2},
                        {"device_id":"plc-01","type":"normal","ts":3},
                        {"device_id":"plc-01","type":"anomaly","ts":4}]
        min_run: Minimum trailing anomaly run length to include in results.  e.g. 3

    Returns:
        List of {"device_id": str, "run_length": int}, sorted by run_length descending.
        e.g. [{"device_id":"rtu-05","run_length":5}, {"device_id":"plc-01","run_length":3}]
        Devices with a trailing run shorter than min_run are excluded.
    """
    # Bucket all events by device so we can process each independently
    # e.g. {"plc-01": [{"device_id":"plc-01","type":"anomaly","ts":1}, ...], "rtu-05": [...]}
    device_events: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        device_events[e["device_id"]].append(e)

    results = []
    for device_id, dev_events in device_events.items():
        # Sort chronologically so reversed() gives us newest-first
        dev_events.sort(key=lambda e: e["ts"])

        # Scan backwards from the most recent event.
        # Count ANOMALY events until we hit a NORMAL (which resets the run).
        run_length = 0
        for event in reversed(dev_events):
            if event["status"] == "ANOMALY":
                run_length += 1
            else:
                break   # NORMAL event terminates the trailing anomaly run

        if run_length >= min_run:
            results.append({"device_id": device_id, "run_length": run_length})

    # Most alarming device first; alphabetical tie-break for determinism
    return sorted(results, key=lambda r: (-r["run_length"], r["device_id"]))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SAMPLE_EVENTS = [
    {"device_id": "plc-01", "status": "NORMAL",  "ts": 100},
    {"device_id": "plc-01", "status": "ANOMALY", "ts": 200},
    {"device_id": "plc-01", "status": "ANOMALY", "ts": 300},
    {"device_id": "plc-01", "status": "ANOMALY", "ts": 400},
    {"device_id": "rtu-05", "status": "ANOMALY", "ts": 100},
    {"device_id": "rtu-05", "status": "NORMAL",  "ts": 200},  # resets run
    {"device_id": "rtu-05", "status": "ANOMALY", "ts": 300},
]

SAMPLE_EVENTS_2 = [
    {"device_id": "plc-01", "status": "NORMAL",  "ts": 100},
    {"device_id": "plc-01", "status": "ANOMALY", "ts": 200},
    {"device_id": "plc-01", "status": "ANOMALY", "ts": 300},
    {"device_id": "plc-01", "status": "ANOMALY", "ts": 400},
    {"device_id": "plc-01", "status": "NORMAL", "ts": 4500},
    {"device_id": "rtu-05", "status": "ANOMALY", "ts": 100},
    {"device_id": "rtu-05", "status": "NORMAL",  "ts": 200},  # resets run
    {"device_id": "rtu-05", "status": "ANOMALY", "ts": 300},
]

def test_detects_long_run():
    result = detect_consecutive_anomalies(SAMPLE_EVENTS, min_run=3)
    assert len(result) == 1
    assert result[0]["device_id"] == "plc-01"
    assert result[0]["run_length"] == 3

def test_detects_long_run_2():
    result = detect_consecutive_anomalies(SAMPLE_EVENTS_2, min_run=3)
    assert len(result) == 0
    # assert len(result) == 1
    # assert result[0]["device_id"] == "plc-01"
    # assert result[0]["run_length"] == 3


def test_reset_by_normal_event():
    result = detect_consecutive_anomalies(SAMPLE_EVENTS, min_run=1)
    rtu_results = [r for r in result if r["device_id"] == "rtu-05"]
    # rtu-05's trailing run is only 1 (the NORMAL at ts=200 resets it)
    assert rtu_results[0]["run_length"] == 1


def test_sorted_by_run_length_desc():
    events = [
        {"device_id": "a", "status": "ANOMALY", "ts": i} for i in range(5)
    ] + [
        {"device_id": "b", "status": "ANOMALY", "ts": i} for i in range(2)
    ]
    result = detect_consecutive_anomalies(events, min_run=1)
    assert result[0]["device_id"] == "a"
    assert result[0]["run_length"] == 5


def test_empty_input():
    assert detect_consecutive_anomalies([]) == []


def test_all_normal():
    events = [{"device_id": "d1", "status": "NORMAL", "ts": i} for i in range(5)]
    assert detect_consecutive_anomalies(events, min_run=1) == []


def test_min_run_threshold():
    events = [
        {"device_id": "d1", "status": "ANOMALY", "ts": 1},
        {"device_id": "d1", "status": "ANOMALY", "ts": 2},
    ]
    assert detect_consecutive_anomalies(events, min_run=3) == []       # run=2, need 3
    assert len(detect_consecutive_anomalies(events, min_run=2)) == 1   # run=2, need 2 ✓


if __name__ == "__main__":
    test_detects_long_run()
    test_detects_long_run_2()
    test_reset_by_normal_event()
    test_sorted_by_run_length_desc()
    test_empty_input()
    test_all_normal()
    test_min_run_threshold()
    print("All tests passed.")
