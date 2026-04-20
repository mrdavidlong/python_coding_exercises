"""
Problem: Process an ordered event log to track each device's current state.

State machine diagram:
---------------------------------------------------------------------------

                    connected / recovered
         ┌──────────────────────────────────────┐
         │                                      │
         ▼          degraded                    │
  UNKNOWN ──► ONLINE ──────────► DEGRADED ──────┘
                 │                   │
                 │ disconnected      │ disconnected
                 └──────┐    ┌───────┘
                         ▼  ▼
                        OFFLINE
                           │
                           │ connected
                           ▼
                         ONLINE  (re-entry)

  - Every new device starts in the implicit UNKNOWN state.
  - Invalid transitions (e.g. ONLINE → ONLINE, OFFLINE → DEGRADED) are
    rejected with an error message but do NOT crash processing.
  - Events are processed in timestamp order even if the input is unsorted.

Valid states: UNKNOWN → ONLINE → DEGRADED → OFFLINE
Valid transitions:
    UNKNOWN   → ONLINE, OFFLINE
    ONLINE    → DEGRADED, OFFLINE
    DEGRADED  → ONLINE, OFFLINE
    OFFLINE   → ONLINE

Invalid transitions should be logged as errors but not crash the processor.

Example input:
    events = [
        {"device_id": "plc-01", "event": "connected",   "ts": 1000},
        {"device_id": "plc-01", "event": "degraded",    "ts": 1100},
        {"device_id": "plc-01", "event": "recovered",   "ts": 1200},
        {"device_id": "plc-01", "event": "disconnected","ts": 1300},
        {"device_id": "rtu-05", "event": "connected",   "ts": 1000},
    ]

Expected final states:  {"plc-01": "OFFLINE", "rtu-05": "ONLINE"}
"""

from typing import Any

# Map incoming event names to the state they produce
EVENT_TO_STATE: dict[str, str] = {
    "connected":    "ONLINE",
    "degraded":     "DEGRADED",
    "recovered":    "ONLINE",    # 'recovered' and 'connected' both land in ONLINE
    "disconnected": "OFFLINE",
}

# Whitelist of legal (from_state, to_state) pairs stored as a set for O(1) lookup.
# Any pair not here is an invalid transition.
VALID_TRANSITIONS: set[tuple[str, str]] = {
    ("UNKNOWN",  "ONLINE"),
    ("UNKNOWN",  "OFFLINE"),
    ("ONLINE",   "DEGRADED"),
    ("ONLINE",   "OFFLINE"),
    ("DEGRADED", "ONLINE"),
    ("DEGRADED", "OFFLINE"),
    ("OFFLINE",  "ONLINE"),
}


def process_device_events(
    events: list[dict[str, Any]],
) -> tuple[dict[str, str], list[str]]:
    """Replay a sequence of device events through the state machine.

    Processing steps for each event:
      1. Look up the target state from EVENT_TO_STATE.
      2. Get the device's current state (default "UNKNOWN" for new devices).
      3. Check if (current → target) is in VALID_TRANSITIONS.
      4. If valid: update the state. If invalid: append an error, keep old state.

    Args:
        events: List of event dicts with "device_id" (str), "event_type" (str), "ts" (float).
                Processed in the order given (caller should sort by ts first if needed).
                e.g. [{"device_id":"plc-01","event_type":"connected","ts":100},
                       {"device_id":"plc-01","event_type":"degraded","ts":200},
                       {"device_id":"plc-01","event_type":"disconnected","ts":300}]

    Returns:
        Tuple of (states, errors):
          states: dict mapping device_id → current state after all events.
                  e.g. {"plc-01": "OFFLINE"}
          errors: list of error strings for invalid transitions.
                  e.g. ["plc-01: invalid transition OFFLINE → DEGRADED at ts=400"]
    """
    # Plain dict (not defaultdict): "UNKNOWN" is a meaningful domain state, not a
    # safe auto-fill. Using .get(device_id, "UNKNOWN") only reads — it does NOT
    # create a spurious entry. defaultdict would silently create entries on typos.
    states: dict[str, str] = {}  # device_id → current state
    errors: list[str] = []

    # Sort by timestamp so out-of-order delivery doesn't corrupt state
    for event in sorted(events, key=lambda e: e["ts"]):
        device_id  = event["device_id"]
        event_name = event["event"]

        # Step 1: translate event name → target state
        new_state = EVENT_TO_STATE.get(event_name)
        if new_state is None:
            errors.append(f"Unknown event '{event_name}' for {device_id} at ts={event['ts']}")
            continue  # skip — can't determine target state

        # Step 2: look up current state; new devices default to UNKNOWN
        current = states.get(device_id, "UNKNOWN")

        # Step 3: validate the transition
        if (current, new_state) not in VALID_TRANSITIONS:
            errors.append(
                f"Invalid transition {current}→{new_state} for {device_id} at ts={event['ts']}"
            )
            continue  # reject — leave state unchanged

        # Step 4: apply the transition
        states[device_id] = new_state

    return states, errors


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SAMPLE_EVENTS = [
    {"device_id": "plc-01", "event": "connected",    "ts": 1000},
    {"device_id": "plc-01", "event": "degraded",     "ts": 1100},
    {"device_id": "plc-01", "event": "recovered",    "ts": 1200},
    {"device_id": "plc-01", "event": "disconnected", "ts": 1300},
    {"device_id": "rtu-05", "event": "connected",    "ts": 1000},
]


def test_final_states():
    states, _ = process_device_events(SAMPLE_EVENTS)
    assert states["plc-01"] == "OFFLINE"
    assert states["rtu-05"] == "ONLINE"


def test_no_errors_on_valid_events():
    _, errors = process_device_events(SAMPLE_EVENTS)
    assert errors == []


def test_invalid_transition_generates_error():
    events = [
        {"device_id": "plc-01", "event": "connected", "ts": 1000},
        {"device_id": "plc-01", "event": "connected", "ts": 1001},  # ONLINE→ONLINE not allowed
    ]
    states, errors = process_device_events(events)
    assert len(errors) == 1
    assert states["plc-01"] == "ONLINE"  # state unchanged after rejected transition


def test_unknown_event_generates_error():
    events = [{"device_id": "plc-01", "event": "rebooted", "ts": 1000}]
    _, errors = process_device_events(events)
    assert any("Unknown event" in e for e in errors)


def test_new_device_starts_as_unknown():
    # UNKNOWN → ONLINE is a valid transition, so this should succeed
    events = [{"device_id": "new-dev", "event": "connected", "ts": 1000}]
    states, _ = process_device_events(events)
    assert states["new-dev"] == "ONLINE"


def test_empty_events():
    states, errors = process_device_events([])
    assert states == {} and errors == []


if __name__ == "__main__":
    test_final_states()
    test_no_errors_on_valid_events()
    test_invalid_transition_generates_error()
    test_unknown_event_generates_error()
    test_new_device_starts_as_unknown()
    test_empty_events()
    print("All tests passed.")
