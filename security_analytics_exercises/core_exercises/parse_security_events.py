"""
Problem: Given a list of security event dicts, filter to those at or above a
minimum severity level and return only the requested fields.

Severity order: INFO < LOW < MEDIUM < HIGH < CRITICAL

Example input:
    events = [
        {"id": "e1", "device_id": "plc-01", "severity": "HIGH", "type": "auth_failure", "ts": 1700000001},
        {"id": "e2", "device_id": "plc-02", "severity": "INFO", "type": "heartbeat",    "ts": 1700000002},
        {"id": "e3", "device_id": "plc-01", "severity": "CRITICAL", "type": "cmd_inject", "ts": 1700000003},
    ]
    parse_security_events(events, min_severity="HIGH", fields=["id", "device_id", "type"])

Expected output:
    [
        {"id": "e1", "device_id": "plc-01", "type": "auth_failure"},
        {"id": "e3", "device_id": "plc-01", "type": "cmd_inject"},
    ]
"""

from typing import Any

SEVERITY_RANK: dict[str, int] = {
    "INFO": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def parse_security_events(
    events: list[dict[str, Any]],
    min_severity: str,
    fields: list[str],
) -> list[dict[str, Any]]:
    """Filter events by minimum severity and project to requested fields.

    Severity comparison is done numerically via SEVERITY_RANK so we avoid
    string ordering ("HIGH" < "INFO" alphabetically, which would be wrong).
    Unknown severity strings default to rank 0 (INFO-equivalent).

    Args:
        events:       List of event dicts. Each must have a "severity" key.
                      e.g. [{"id":"e1","device_id":"plc-01","severity":"HIGH","type":"auth_failure"}]
        min_severity: Minimum severity to include (case-insensitive).
                      e.g. "HIGH"  → keeps HIGH and CRITICAL, drops INFO/LOW/MEDIUM
        fields:       Keys to keep in each returned dict.
                      e.g. ["id", "device_id", "type"]

    Returns:
        Filtered list with only the requested fields present.
        e.g. [{"id":"e1","device_id":"plc-01","type":"auth_failure"}]
    """
    # Convert the caller's threshold string to a numeric rank once, outside the loop
    threshold = SEVERITY_RANK.get(min_severity.upper(), 0)
    result = []
    for event in events:
        # Default missing/unknown severity to INFO (rank 0) rather than raising
        rank = SEVERITY_RANK.get(event.get("severity", "INFO").upper(), 0)
        if rank >= threshold:
            # Dict comprehension: only keep fields the caller asked for,
            # and only if they actually exist on this event (no KeyErrors)
            result.append({k: event[k] for k in fields if k in event})
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SAMPLE_EVENTS = [
    {"id": "e1", "device_id": "plc-01", "severity": "HIGH",     "type": "auth_failure", "ts": 1700000001},
    {"id": "e2", "device_id": "plc-02", "severity": "INFO",     "type": "heartbeat",    "ts": 1700000002},
    {"id": "e3", "device_id": "plc-01", "severity": "CRITICAL", "type": "cmd_inject",   "ts": 1700000003},
    {"id": "e4", "device_id": "rtu-05", "severity": "MEDIUM",   "type": "config_change","ts": 1700000004},
    {"id": "e5", "device_id": "rtu-05", "severity": "LOW",      "type": "scan_detected","ts": 1700000005},
]


def test_filters_by_min_severity():
    result = parse_security_events(SAMPLE_EVENTS, min_severity="HIGH", fields=["id", "device_id", "type"])
    ids = [r["id"] for r in result]
    assert ids == ["e1", "e3"], f"Expected [e1, e3], got {ids}"
    # Ensure only requested fields are present
    for r in result:
        assert set(r.keys()) == {"id", "device_id", "type"}


def test_includes_all_at_info():
    result = parse_security_events(SAMPLE_EVENTS, min_severity="INFO", fields=["id"])
    assert len(result) == 5


def test_critical_only():
    result = parse_security_events(SAMPLE_EVENTS, min_severity="CRITICAL", fields=["id"])
    assert [r["id"] for r in result] == ["e3"]


def test_missing_severity_treated_as_info():
    events = [{"id": "x", "type": "unknown"}]  # no 'severity' key
    result = parse_security_events(events, min_severity="INFO", fields=["id"])
    assert result == [{"id": "x"}]


def test_missing_requested_field_omitted():
    events = [{"id": "x", "severity": "HIGH"}]  # no 'type' key
    result = parse_security_events(events, min_severity="HIGH", fields=["id", "type"])
    assert result == [{"id": "x"}]


if __name__ == "__main__":
    test_filters_by_min_severity()
    test_includes_all_at_info()
    test_critical_only()
    test_missing_severity_treated_as_info()
    test_missing_requested_field_omitted()
    print("All tests passed.")
