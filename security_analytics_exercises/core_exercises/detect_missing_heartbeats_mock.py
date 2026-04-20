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


# ⏺ Line 45 uses < cutoff (strict less than) instead of <= cutoff. A heartbeat at exactly the cutoff passes through as healthy, but the test expects it to be flagged as missing.

#   Also there's a second bug on line 38 — the condition is backwards. It keeps the existing entry when its ts is greater, meaning it retains the newer heartbeat and discards the older one. That's actually correct for "keep
#   latest", but the logic reads confusingly — it should be h["ts"] > existing["ts"] to replace with the newer one.

#   Fix both:

# ⏺ Update(detect_missing_heartbeats_mock.py)
#   ⎿  Added 1 line, removed 1 line
#       35          existing = latest.get(device_id) #remember using .get instead of latest[h[device_id]]
#       36          if existing is None:
#       37              latest[device_id] = h #remember, just use device_id instead of existing[device_id]
#       38 -        elif latest[device_id]["ts"] > h["ts"]:                                                                                                                                                                 
#       38 +        elif h["ts"] > latest[device_id]["ts"]:  # keep the newer heartbeat                                                                                                                                     
#       39              latest[device_id] = h
#       40  
#       41      result = []

# ⏺ Update(detect_missing_heartbeats_mock.py)
#   ⎿  Added 1 line, removed 1 line
#       42      for d in expected_devices:
#       43          if latest.get(d) is None:
#       44              result.append(d)
#       45 -        elif (latest[d].get("ts", float("-inf")) < cutoff):                                                                                                                                                     
#       45 +        elif (latest[d].get("ts", float("-inf")) <= cutoff):  # at boundary = still missing                                                                                                                     
#       46              result.append(d)
#       47      result.sort()
#       48      return result

# ⏺ Bash(python detect_missing_heartbeats_mock.py)

def detect_missing_heartbeats(
    expected_devices: list[str],
    heartbeats: list[dict[str, Any]],
    timeout_seconds: int = 300,
    reference_ts: float | None = None,
) -> list[str]:
    if reference_ts is None:
        reference_ts = max((h["ts"] for h in heartbeats), default=0)

    cutoff = reference_ts - timeout_seconds
    latest: dict[str, dict[str, Any]] = {}
    for h in heartbeats:
        device_id = h["device_id"]
        existing = latest.get(device_id) #remember using .get instead of latest[h[device_id]]
        if existing is None:
            latest[device_id] = h #remember, just use device_id instead of existing[device_id]
        elif h["ts"] > latest[device_id]["ts"]:  #remember: keep the newer heartbeat
            latest[device_id] = h
        
    result = []
    for d in expected_devices:
        if latest.get(d) is None:
            result.append(d)
        elif (latest[d].get("ts", float("-inf")) <= cutoff):  #remember: at boundary = still missing
            result.append(d)
    #result.sort()  list.sort() modifies the existing list in-place, while sorted() creates a new sorted list from any iterable
    #return result
    #
    # return [
    #     d
    #     for d in expected_devices
    #     if latest.get(d) is None or (latest[d].get("ts", float("-inf")) <= cutoff)
    # ].sort()
        
    return sorted(result)




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
