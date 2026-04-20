"""
Problem: Classify raw security events into LOW / MEDIUM / HIGH / CRITICAL
based on business rules applied to event fields.

Rules (evaluated in order, first match wins):
  CRITICAL  — alert_type is in CRITICAL_TYPES
  HIGH      — failed_attempts >= 5  OR  source is "external"
  MEDIUM    — alert_type is in MEDIUM_TYPES  OR  failed_attempts >= 2
  LOW       — everything else

Example input:
    event = {"alert_type": "cmd_inject", "source": "internal", "failed_attempts": 1}
Expected output:  "CRITICAL"

    event = {"alert_type": "login", "source": "external", "failed_attempts": 1}
Expected output:  "HIGH"
"""

from typing import Any

CRITICAL_TYPES = {"cmd_inject", "firmware_tamper", "safety_override"}
MEDIUM_TYPES   = {"config_change", "port_scan", "protocol_anomaly"}


def classify_severity(event: dict[str, Any]) -> str:
    """Classify a single event into CRITICAL / HIGH / MEDIUM / LOW.

    Rules are evaluated in priority order — first match returns immediately.
    CRITICAL is checked before HIGH so a cmd_inject from an external source
    with 10 failed attempts still gets CRITICAL, not HIGH.

    Args:
        event: Dict with optional keys:
                 "alert_type"      (str)  e.g. "cmd_inject", "auth_failure"
                 "source"          (str)  e.g. "external", "internal"
                 "failed_attempts" (int)  e.g. 7
               Missing keys default to: alert_type="", source="internal", failed_attempts=0

    Returns:
        One of "CRITICAL", "HIGH", "MEDIUM", "LOW".
        e.g. classify_severity({"alert_type":"cmd_inject"}) → "CRITICAL"
        e.g. classify_severity({"source":"external"})       → "HIGH"
        e.g. classify_severity({"alert_type":"heartbeat"})  → "LOW"
    """
    alert_type      = event.get("alert_type", "")
    source          = event.get("source", "internal")
    failed_attempts = event.get("failed_attempts", 0)

    # CRITICAL: specific dangerous OT operation types — highest priority
    if alert_type in CRITICAL_TYPES:
        return "CRITICAL"

    # HIGH: many failed attempts (brute-force indicator) OR external origin
    if failed_attempts >= 5 or source == "external":
        return "HIGH"

    # MEDIUM: known suspicious but lower-risk types, OR moderate failure count
    if alert_type in MEDIUM_TYPES or failed_attempts >= 2:
        return "MEDIUM"

    # LOW: everything else — likely benign but still worth logging
    return "LOW"


def classify_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Classify a list of events and attach a 'severity' field to each.

    Uses {**e, ...} to create a new dict — the originals are never mutated.

    Args:
        events: List of event dicts. Each is passed to classify_severity().
                e.g. [{"alert_type":"cmd_inject"}, {"source":"external"}]

    Returns:
        New list of dicts with "severity" added to each.
        e.g. [{"alert_type":"cmd_inject","severity":"CRITICAL"},
               {"source":"external","severity":"HIGH"}]

    # Alternative without ** spread:
    #   result = []
    #   for e in events:
    #       copy = e.copy()          # shallow copy so original is untouched
    #       copy["severity"] = classify_severity(e)
    #       result.append(copy)
    #   return result
    """
    return [{**e, "severity": classify_severity(e)} for e in events]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_critical_type():
    assert classify_severity({"alert_type": "cmd_inject"}) == "CRITICAL"
    assert classify_severity({"alert_type": "safety_override"}) == "CRITICAL"


def test_high_external_source():
    assert classify_severity({"alert_type": "login", "source": "external"}) == "HIGH"


def test_high_many_failures():
    assert classify_severity({"alert_type": "login", "failed_attempts": 5}) == "HIGH"


def test_medium_type():
    assert classify_severity({"alert_type": "config_change"}) == "MEDIUM"


def test_medium_two_failures():
    assert classify_severity({"alert_type": "login", "failed_attempts": 2}) == "MEDIUM"


def test_low_default():
    assert classify_severity({"alert_type": "heartbeat"}) == "LOW"
    assert classify_severity({}) == "LOW"


def test_critical_takes_priority_over_high_conditions():
    # Even with external source, cmd_inject should be CRITICAL not HIGH
    event = {"alert_type": "cmd_inject", "source": "external", "failed_attempts": 10}
    assert classify_severity(event) == "CRITICAL"


def test_classify_events_enriches_list():
    events = [{"alert_type": "cmd_inject"}, {"alert_type": "heartbeat"}]
    result = classify_events(events)
    assert result[0]["severity"] == "CRITICAL"
    assert result[1]["severity"] == "LOW"
    # Original dicts not mutated
    assert "severity" not in events[0]


if __name__ == "__main__":
    test_critical_type()
    test_high_external_source()
    test_high_many_failures()
    test_medium_type()
    test_medium_two_failures()
    test_low_default()
    test_critical_takes_priority_over_high_conditions()
    test_classify_events_enriches_list()
    print("All tests passed.")
