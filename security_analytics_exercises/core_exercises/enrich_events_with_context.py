"""
Problem: Enrich a stream of events with device metadata from a lookup table.
Each event has a device_id; the lookup table maps device_id → metadata dict.
Merge the metadata into each event. Events for unknown devices get a flag.

Example input:
    events = [
        {"id": "e1", "device_id": "plc-01", "type": "auth_failure"},
        {"id": "e2", "device_id": "unknown-99", "type": "scan"},
    ]
    device_metadata = {
        "plc-01": {"ds": "Plant A", "criticality": "HIGH", "owner": "ops-team"},
    }

Expected output:
    [
        {"id": "e1", "device_id": "plc-01", "type": "auth_failure",
         "site": "Plant A", "criticality": "HIGH", "owner": "ops-team", "known_device": True},
        {"id": "e2", "device_id": "unknown-99", "type": "scan", "known_device": False},
    ]
"""

from typing import Any


def enrich_events(
    events: list[dict[str, Any]],
    device_metadata: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Join each event with its device metadata by device_id.

    Merge precedence — event fields win over metadata fields on collision:
      {**meta, **event}   ← later dict (**event) overwrites earlier (**meta)

    unknown_device flag lets downstream consumers quickly filter rogue devices
    without re-querying the metadata table.

    Args:
        events:          List of event dicts, each with a "device_id" key.
                         e.g. [{"id":"e1","device_id":"plc-01","type":"auth_failure"}]
        device_metadata: Lookup table: device_id → metadata dict.
                         e.g. {"plc-01":{"site":"plant-A","criticality":"high"}}

    Returns:
        New list of enriched dicts with metadata merged in and "known_device" flag added.
        e.g. [{"id":"e1","device_id":"plc-01","type":"auth_failure",
                "site":"plant-A","criticality":"high","known_device":True}]
        Unknown devices get {"known_device": False} and no metadata fields.
    """
    enriched = []
    for event in events:
        device_id = event.get("device_id")
        meta      = device_metadata.get(device_id)  # None if device is unknown

        if meta:
            # Spread order: meta first, then event — event keys override meta keys
            enriched.append({**meta, **event, "known_device": True}) #remember, it's : not =
        else:
            # Unknown device: pass event through unchanged, just add the flag
            enriched.append({**event, "known_device": False})
    return enriched


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

DEVICE_META = {
    "plc-01": {"site": "Plant A", "criticality": "HIGH", "owner": "ops-team"},
    "rtu-05": {"site": "Plant B", "criticality": "MEDIUM", "owner": "maint-team"},
}

EVENTS = [
    {"id": "e1", "device_id": "plc-01", "type": "auth_failure"},
    {"id": "e2", "device_id": "unknown-99", "type": "scan"},
    {"id": "e3", "device_id": "rtu-05", "type": "heartbeat"},
]


def test_known_device_enriched():
    result = enrich_events(EVENTS, DEVICE_META)
    e1 = next(e for e in result if e["id"] == "e1")
    assert e1["site"] == "Plant A"
    assert e1["criticality"] == "HIGH"
    assert e1["known_device"] is True


def test_unknown_device_flagged():
    result = enrich_events(EVENTS, DEVICE_META)
    e2 = next(e for e in result if e["id"] == "e2")
    assert e2["known_device"] is False
    assert "site" not in e2


def test_event_fields_win_on_collision():
    # If event already has 'criticality', it should not be overwritten by metadata
    events = [{"id": "x", "device_id": "plc-01", "criticality": "CUSTOM"}]
    result = enrich_events(events, DEVICE_META)
    assert result[0]["criticality"] == "CUSTOM"


def test_original_events_not_mutated():
    original_len = len(EVENTS[0])
    enrich_events(EVENTS, DEVICE_META)
    assert len(EVENTS[0]) == original_len


def test_empty_events():
    assert enrich_events([], DEVICE_META) == []


def test_empty_metadata():
    result = enrich_events(EVENTS, {})
    assert all(e["known_device"] is False for e in result)


if __name__ == "__main__":
    test_known_device_enriched()
    test_unknown_device_flagged()
    test_event_fields_win_on_collision()
    test_original_events_not_mutated()
    test_empty_events()
    test_empty_metadata()
    print("All tests passed.")
