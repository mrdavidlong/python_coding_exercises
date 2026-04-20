"""
Problem: Given a list of expected device IDs and a heartbeat log, find all
devices that have NOT sent a heartbeat within the last `timeout_seconds`.

Example input:
    expected_devices = ["plc-01", "plc-02", "rtu-05", "hmi-03"]
    heartbeats = [
        {"device_id": "plc-01", "ts": 1700010000},
        {"device_id": "rtu-05", "ts": 1700009800},
        {"device_id": "hmi-03", "ts": 1699999999},  # too old
    ]
    detect_missing_heartbeats(expected_devices, heartbeats, timeout_seconds=300, reference_ts=1700010100)

Expected output:  ["hmi-03", "plc-02"]   # sorted, plc-02 never checked in
"""

from __future__ import annotations

from typing import Any


def detect_missing_heartbeats(
    expected_devices: list[str],
    heartbeats: list[dict[str, Any]],
    timeout_seconds: int = 300,
    reference_ts: float | None = None,
) -> list[str]:
    """Find devices that have not sent a heartbeat within the timeout window.

    Two failure modes are caught:
      1. Device never reported — not in the heartbeat log at all.
      2. Device reported, but its most recent heartbeat is stale (too old).

    A heartbeat exactly at the cutoff (reference_ts - timeout_seconds) is
    still considered missing — the device must report AFTER the cutoff.

    Args:
        expected_devices: All device IDs that should be reporting.
                          e.g. ["plc-01", "plc-02", "rtu-05", "hmi-03"]
        heartbeats:       Log of heartbeat events, each with "device_id" and "ts".
                          e.g. [{"device_id":"plc-01","ts":1700010000},
                                 {"device_id":"hmi-03","ts":1699999999}]
        timeout_seconds:  Max allowed silence before a device is flagged.  e.g. 300
        reference_ts:     Epoch seconds for "now". Defaults to max(ts) in heartbeats.
                          e.g. 1700010100

    Returns:
        Sorted list of device_ids that are missing or stale.
        e.g. ["hmi-03", "plc-02"]   # hmi-03 stale, plc-02 never reported
    """
    if reference_ts is None:
        # default=0 handles the edge case of an empty heartbeat list
        #remember
        #  note:
        #   1. Empty list: if heartbeats is empty, max() with no arguments raises ValueError. The default=0 parameter handles that — it's max()'s own built-in fallback for empty iterables. Your version would also raise on empty because
        #    the generator produces nothing.
        #   2. Missing "ts" key: h.get("ts", 0) guards against a heartbeat dict that has no "ts" field, treating it as timestamp 0. But that's a malformed input — silently treating it as epoch time could hide bugs. Better to let it
        #   raise KeyError so you know the data is bad.
        #   So default=0 on max() is the right guard (empty list is a valid input), while h.get("ts", 0) would be masking a data quality problem.
        reference_ts = max((h["ts"] for h in heartbeats), default=0) #remember to add the parenthesis around the first param, and add the default=0

    # Any heartbeat older than this is too stale to count
    cutoff = reference_ts - timeout_seconds

    # Plain dict (not defaultdict): the custom sentinel float("-inf") is the
    # business logic — it means "device never reported", which is different from 0.0.
    # defaultdict(float) would give 0.0, a real-looking timestamp that breaks the
    # comparison. When the default value isn't uniform, plain dict + .get() wins.
    # e.g. {"plc-01": 1700010000.0, "rtu-05": 1700009801.0}  — only devices that reported
    latest: dict[str, float] = {} #remember, only stores the timestamp as value, not the whole object
    for h in heartbeats:
        device_id = h["device_id"]
        # Keep only the latest ts — earlier heartbeats from the same device don't help
        if h["ts"] > latest.get(device_id, float("-inf")): #remember -1.0 means one second before that, so use float("-inf"), # keep the newer heartbeat 
            latest[device_id] = h["ts"]

    # float("-inf") as default means: "device never reported" → always ≤ cutoff → missing
    missing = [
        device_id
        for device_id in expected_devices
        if latest.get(device_id, float("-inf")) <= cutoff #remember:  # at boundary = still missing
    ]
    return sorted(missing)   # sorted for deterministic output and easy assertion in tests


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

EXPECTED = ["plc-01", "plc-02", "rtu-05", "hmi-03"]
# cutoff = REF_TS - TIMEOUT = 1700009800; rtu-05 is 1s inside the window
HEARTBEATS = [
    {"device_id": "plc-01", "ts": 1700010000},
    {"device_id": "rtu-05", "ts": 1700009801},  # 1s after cutoff → healthy
    {"device_id": "hmi-03", "ts": 1699999999},  # stale
]
REF_TS  = 1700010100
TIMEOUT = 300


def test_detects_stale_and_absent():
    result = detect_missing_heartbeats(EXPECTED, HEARTBEATS, TIMEOUT, REF_TS)
    assert "hmi-03" in result   # stale heartbeat
    assert "plc-02" in result   # never checked in
    assert "plc-01" not in result
    assert "rtu-05" not in result


def test_result_is_sorted():
    result = detect_missing_heartbeats(EXPECTED, HEARTBEATS, TIMEOUT, REF_TS)
    assert result == sorted(result)


def test_all_healthy():
    heartbeats = [{"device_id": d, "ts": REF_TS - 10} for d in EXPECTED]
    result = detect_missing_heartbeats(EXPECTED, heartbeats, TIMEOUT, REF_TS)
    assert result == []


def test_all_missing():
    result = detect_missing_heartbeats(EXPECTED, [], TIMEOUT, REF_TS)
    assert sorted(result) == sorted(EXPECTED)


def test_exactly_at_boundary():
    # A heartbeat exactly at cutoff (REF_TS - TIMEOUT) is still missing
    cutoff = REF_TS - TIMEOUT
    heartbeats = [{"device_id": "plc-01", "ts": cutoff}]
    result = detect_missing_heartbeats(["plc-01"], heartbeats, TIMEOUT, REF_TS)
    assert result == ["plc-01"]  # cutoff is not > cutoff


def test_one_second_past_cutoff():
    cutoff = REF_TS - TIMEOUT
    heartbeats = [{"device_id": "plc-01", "ts": cutoff + 1}]
    result = detect_missing_heartbeats(["plc-01"], heartbeats, TIMEOUT, REF_TS)
    assert result == []  # ts > cutoff → healthy


if __name__ == "__main__":
    test_detects_stale_and_absent()
    test_result_is_sorted()
    test_all_healthy()
    test_all_missing()
    test_exactly_at_boundary()
    test_one_second_past_cutoff()
    print("All tests passed.")
