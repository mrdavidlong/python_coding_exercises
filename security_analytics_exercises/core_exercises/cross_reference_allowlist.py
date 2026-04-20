"""
Problem: The security analytics platform maintains an approved asset allowlist. Any
event from a device NOT on the allowlist should be flagged as a potential
rogue/unknown device — a high-priority finding in OT environments.

Given a list of events and an allowlist of approved device IDs, return:
    - approved_events:  events from known devices
    - flagged_events:   events from unknown devices (enriched with "flag" field)
    - unknown_devices:  sorted list of unique unknown device IDs

Example input:
    allowlist = {"plc-01", "plc-02", "rtu-05"}
    events = [
        {"id": "e1", "device_id": "plc-01",    "type": "heartbeat"},
        {"id": "e2", "device_id": "rogue-99",  "type": "scan"},
        {"id": "e3", "device_id": "plc-02",    "type": "auth_failure"},
        {"id": "e4", "device_id": "unknown-42","type": "connect"},
    ]

Expected:
    approved_events: [e1, e3]
    flagged_events:  [e2 + flag, e4 + flag]
    unknown_devices: ["rogue-99", "unknown-42"]
"""

from typing import Any


def cross_reference_allowlist(
    events: list[dict[str, Any]],
    allowlist: set[str],
) -> dict[str, Any]:
    """Partition events into approved (known device) and flagged (unknown device) groups.

    The allowlist should be a set (not a list) for O(1) membership checks.
    Flagged events are copies so original dicts are never mutated.

    Args:
        events:    List of event dicts, each with a "device_id" key.
                   e.g. [{"id":"e1","device_id":"plc-01","type":"heartbeat"},
                          {"id":"e2","device_id":"rogue-99","type":"scan"}]
        allowlist: Set of approved device IDs.
                   e.g. {"plc-01", "plc-02", "rtu-05"}

    Returns:
        Dict with three keys:
          "approved_events":  events from known devices (unchanged)
          "flagged_events":   events from unknown devices, each enriched with {"flag":"UNKNOWN_DEVICE"}
          "unknown_devices":  sorted list of unique unknown device_ids
        e.g. {"approved_events":[{"id":"e1",...}],
               "flagged_events":[{"id":"e2","device_id":"rogue-99","flag":"UNKNOWN_DEVICE"}],
               "unknown_devices":["rogue-99"]}
    """
    approved_events:    list[dict] = []
    flagged_events:     list[dict] = []
    unknown_device_ids: set[str]   = set()   # deduplicate across multiple events

    for event in events:
        device_id = event.get("device_id", "")

        if device_id in allowlist:
            # Known device — pass through unchanged (no copy needed here)
            approved_events.append(event)
        else:
            # Unknown device — add flag field via spread (original dict untouched)
            flagged_events.append({**event, "flag": "UNKNOWN_DEVICE"})
            if device_id:   # skip empty string device_ids
                unknown_device_ids.add(device_id)

    return {
        "approved_events":  approved_events,
        "flagged_events":   flagged_events,
        "unknown_devices":  sorted(unknown_device_ids),   # sorted for stable output
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

ALLOWLIST = {"plc-01", "plc-02", "rtu-05"}
EVENTS = [
    {"id": "e1", "device_id": "plc-01",     "type": "heartbeat"},
    {"id": "e2", "device_id": "rogue-99",   "type": "scan"},
    {"id": "e3", "device_id": "plc-02",     "type": "auth_failure"},
    {"id": "e4", "device_id": "unknown-42", "type": "connect"},
]


def test_approved_events():
    result = cross_reference_allowlist(EVENTS, ALLOWLIST)
    ids = {e["id"] for e in result["approved_events"]}
    assert ids == {"e1", "e3"}


def test_flagged_events():
    result = cross_reference_allowlist(EVENTS, ALLOWLIST)
    ids = {e["id"] for e in result["flagged_events"]}
    assert ids == {"e2", "e4"}


def test_flagged_events_have_flag_field():
    result = cross_reference_allowlist(EVENTS, ALLOWLIST)
    assert all(e["flag"] == "UNKNOWN_DEVICE" for e in result["flagged_events"])


def test_unknown_devices_sorted():
    result = cross_reference_allowlist(EVENTS, ALLOWLIST)
    assert result["unknown_devices"] == ["rogue-99", "unknown-42"]


def test_all_approved():
    events = [{"id": "e1", "device_id": "plc-01"}]
    result = cross_reference_allowlist(events, ALLOWLIST)
    assert result["flagged_events"] == []
    assert result["unknown_devices"] == []


def test_all_unknown():
    events = [{"id": "e1", "device_id": "evil-device"}]
    result = cross_reference_allowlist(events, ALLOWLIST)
    assert result["approved_events"] == []
    assert result["unknown_devices"] == ["evil-device"]


def test_empty_events():
    result = cross_reference_allowlist([], ALLOWLIST)
    assert result["approved_events"] == []
    assert result["flagged_events"]  == []


def test_original_events_not_mutated():
    original_keys = set(EVENTS[1].keys())
    cross_reference_allowlist(EVENTS, ALLOWLIST)
    assert set(EVENTS[1].keys()) == original_keys  # flag not added to original


if __name__ == "__main__":
    test_approved_events()
    test_flagged_events()
    test_flagged_events_have_flag_field()
    test_unknown_devices_sorted()
    test_all_approved()
    test_all_unknown()
    test_empty_events()
    test_original_events_not_mutated()
    print("All tests passed.")
