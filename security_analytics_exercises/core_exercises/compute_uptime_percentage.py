"""
Problem: Given a log of ONLINE/OFFLINE events per device and a fixed observation
window [window_start, window_end], compute each device's uptime percentage.

How uptime calculation works:
---------------------------------------------------------------------------

  window: 0 ────────────────────────────────────────── 1000
                                                       (total = 1000s)

  Event log for plc-01:
    ts=100  ONLINE
    ts=700  OFFLINE

  Timeline reconstruction:
    0 ──── 100 ─────────────────── 700 ──── 1000
    [OFFLINE][←────── ONLINE ──────────][OFFLINE]
       100s         600s                  300s

  Uptime = 600s / 1000s = 60.0%

Inferring the initial state (the tricky part):
---------------------------------------------------------------------------
  We only know what happened INSIDE the window. To compute the interval
  BEFORE the first event, we infer backward from the first event's state:

    First event = ONLINE  → device was OFFLINE before it came online
                             (the ONLINE event is what changed things)
    First event = OFFLINE → device was ONLINE  before it went offline

  This is the "state flip" heuristic: the event represents a CHANGE,
  so the prior state must be the opposite.

Assumptions:
  - Events outside [window_start, window_end] are ignored.
  - Events are re-sorted per device even if the input is partially sorted.

Example input:
    events = [
        {"device_id": "plc-01", "state": "ONLINE",  "ts": 100},
        {"device_id": "plc-01", "state": "OFFLINE", "ts": 700},
    ]
    window = (0, 1000)

Expected: uptime = 600 / 1000 = 60.0%
"""

from collections import defaultdict
from typing import Any


def compute_uptime_percentage(
    events: list[dict[str, Any]],
    window_start: float,
    window_end: float,
) -> dict[str, float]:
    """Compute uptime percentage per device over a fixed observation window.

    Args:
        events:       List of state-change dicts, each with keys:
                        "device_id" (str), "state" ("ONLINE"|"OFFLINE"), "ts" (float)
                      e.g. [{"device_id":"plc-01","state":"ONLINE","ts":100},
                             {"device_id":"plc-01","state":"OFFLINE","ts":700}]
        window_start: Start of the observation window (epoch seconds, inclusive).
                      e.g. 0
        window_end:   End of the observation window (epoch seconds, inclusive).
                      e.g. 1000

    Returns:
        Dict mapping device_id → uptime percentage (0.0–100.0, rounded to 2dp).
        Only devices that have at least one event inside the window are included.
        e.g. {"plc-01": 60.0}   # 600s online out of 1000s window
    """
    window_duration = window_end - window_start
    if window_duration <= 0:
        raise ValueError("window_end must be greater than window_start")

    # Clip events to the window and group per device
    # e.g. {"plc-01": [{"device_id":"plc-01","state":"ONLINE","ts":100}, ...], "rtu-05": [...]}
    device_events: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        if window_start <= e["ts"] <= window_end:
            device_events[e["device_id"]].append(e)

    results: dict[str, float] = {}

    for device_id, dev_events in device_events.items():
        dev_events.sort(key=lambda e: e["ts"])

        # --- Infer the state BEFORE the first event in the window ---
        # If the first event says ONLINE, the device was OFFLINE just before.
        # If the first event says OFFLINE, the device was ONLINE just before.
        current_state = "OFFLINE" if dev_events[0]["state"] == "ONLINE" else "ONLINE"
        prev_ts       = window_start   # start accumulating from the window boundary
        uptime        = 0.0

        # Walk each event, accumulating uptime for intervals where state == ONLINE
        for event in dev_events:
            interval = event["ts"] - prev_ts     # seconds in the current state segment
            if current_state == "ONLINE":
                uptime += interval
            # Transition: adopt the new state and advance the clock
            current_state = event["state"]
            prev_ts       = event["ts"]

        # --- Handle the tail: time between the last event and window_end ---
        if current_state == "ONLINE":
            uptime += window_end - prev_ts

        results[device_id] = round(uptime / window_duration * 100, 2)

    return results


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_basic_uptime():
    events = [
        {"device_id": "plc-01", "state": "ONLINE",  "ts": 100},
        {"device_id": "plc-01", "state": "OFFLINE", "ts": 700},
    ]
    result = compute_uptime_percentage(events, 0, 1000)
    assert result["plc-01"] == 60.0  # 600 / 1000


def test_always_online():
    # First event = ONLINE at window_start → inferred prior = OFFLINE → 0 downtime before
    events = [{"device_id": "d1", "state": "ONLINE", "ts": 0}]
    result = compute_uptime_percentage(events, 0, 100)
    assert result["d1"] == 100.0


def test_always_offline():
    # First event = OFFLINE at window_start → inferred prior = ONLINE → but immediately offline
    events = [{"device_id": "d1", "state": "OFFLINE", "ts": 0}]
    result = compute_uptime_percentage(events, 0, 100)
    assert result["d1"] == 0.0


def test_multiple_transitions():
    events = [
        {"device_id": "d1", "state": "ONLINE",  "ts": 0},
        {"device_id": "d1", "state": "OFFLINE", "ts": 25},
        {"device_id": "d1", "state": "ONLINE",  "ts": 50},
        {"device_id": "d1", "state": "OFFLINE", "ts": 75},
    ]
    result = compute_uptime_percentage(events, 0, 100)
    # ONLINE segments: 0-25 (25s) + 50-75 (25s) = 50s / 100s = 50%
    assert result["d1"] == 50.0


def test_multiple_devices():
    events = [
        {"device_id": "d1", "state": "ONLINE",  "ts": 0},
        {"device_id": "d2", "state": "OFFLINE", "ts": 0},
    ]
    result = compute_uptime_percentage(events, 0, 100)
    assert result["d1"] == 100.0
    assert result["d2"] == 0.0


if __name__ == "__main__":
    test_basic_uptime()
    test_always_online()
    test_always_offline()
    test_multiple_transitions()
    test_multiple_devices()
    print("All tests passed.")
