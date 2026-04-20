"""
Problem: OT maintenance windows should suppress alerts for specific devices during
planned downtime. Given a list of suppression rules and incoming alerts, filter
out any alerts that fall within a rule's time window.

Suppression rule format:
    {
        "rule_id":    "MW-001",
        "device_ids": ["plc-01", "rtu-05"],  # empty list = applies to ALL devices
        "start_ts":   1700000000,
        "end_ts":     1700003600,
        "reason":     "planned maintenance",
    }

An alert is suppressed if:
  1. Its timestamp falls within [start_ts, end_ts] (inclusive), AND
  2. Its device_id matches a device in rule's device_ids, OR device_ids is empty (wildcard)

Return (passed_alerts, suppressed_alerts) tuple.
"""

from typing import Any


def apply_suppression_rules(
    alerts: list[dict[str, Any]],
    rules: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Filter alerts against maintenance window rules, returning (passed, suppressed).

    Matching logic per alert:
      1. Iterate rules in order (rule priority is controlled by list position).
      2. For each rule check: is the alert's ts inside [start_ts, end_ts]?
      3. If yes: does the rule apply to this device?
           - empty device_ids → wildcard (applies to ALL devices)
           - non-empty → device_id must be in the list
      4. First matching rule suppresses the alert and stops evaluation (break).
         This prevents double-suppression and keeps the rule_id attribution clear.

    Suppressed alerts get a "suppressed_by" field for audit attribution.

    Args:
        alerts: List of alert dicts, each with "device_id" (str) and "ts" (float).
                e.g. [{"id":"a1","device_id":"plc-01","ts":1500},
                       {"id":"a2","device_id":"rtu-05","ts":1500}]
        rules:  Ordered list of suppression rule dicts with keys:
                  "rule_id", "device_ids" (list, empty=wildcard),
                  "start_ts", "end_ts", "reason"
                e.g. [{"rule_id":"MW-001","device_ids":["plc-01"],
                        "start_ts":1000,"end_ts":2000,"reason":"firmware update"}]

    Returns:
        Tuple of (passed_alerts, suppressed_alerts).
        Suppressed alerts include the original fields plus "suppressed_by": rule_id.
        e.g. ([{"id":"a2","device_id":"rtu-05","ts":1500}],
               [{"id":"a1","device_id":"plc-01","ts":1500,"suppressed_by":"MW-001"}])
    """
    passed:     list[dict] = []
    suppressed: list[dict] = []

    for alert in alerts:
        device_id    = alert.get("device_id", "")
        ts           = alert.get("ts", 0)
        matched_rule = None

        for rule in rules:
            # Check 1: is the alert timestamp inside the maintenance window?
            in_window = rule["start_ts"] <= ts <= rule["end_ts"]

            # Check 2: does this rule cover this device?
            # `not rule["device_ids"]` is True when the list is empty (wildcard)
            device_match = (
                not rule["device_ids"]         # empty list = applies to all
                or device_id in rule["device_ids"]
            )

            if in_window and device_match:
                matched_rule = rule
                break  # first matching rule wins; stop looking

        if matched_rule:
            # Enrich with attribution so callers know which rule fired
            suppressed.append({**alert, "suppressed_by": matched_rule["rule_id"]})
        else:
            passed.append(alert)   # no rule matched — alert passes through

    return passed, suppressed


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

RULES = [
    {
        "rule_id":    "MW-001",
        "device_ids": ["plc-01"],
        "start_ts":   1000,
        "end_ts":     2000,
        "reason":     "plc-01 firmware update",
    },
    {
        "rule_id":    "MW-002",
        "device_ids": [],  # wildcard — all devices
        "start_ts":   5000,
        "end_ts":     6000,
        "reason":     "network maintenance",
    },
]

ALERTS = [
    {"id": "a1", "device_id": "plc-01", "ts": 1500},   # in MW-001 window
    {"id": "a2", "device_id": "rtu-05", "ts": 1500},   # not in MW-001 (wrong device)
    {"id": "a3", "device_id": "plc-01", "ts": 5500},   # in MW-002 (wildcard)
    {"id": "a4", "device_id": "rtu-05", "ts": 5500},   # in MW-002 (wildcard)
    {"id": "a5", "device_id": "plc-01", "ts": 9000},   # outside all windows
]


def test_alert_in_maintenance_window_suppressed():
    passed, suppressed = apply_suppression_rules(ALERTS, RULES)
    ids = {a["id"] for a in suppressed}
    assert "a1" in ids


def test_alert_outside_window_passed():
    passed, suppressed = apply_suppression_rules(ALERTS, RULES)
    ids = {a["id"] for a in passed}
    assert "a5" in ids


def test_wrong_device_not_suppressed():
    passed, suppressed = apply_suppression_rules(ALERTS, RULES)
    ids = {a["id"] for a in passed}
    assert "a2" in ids  # rtu-05 not in MW-001


def test_wildcard_rule_suppresses_all_devices():
    passed, suppressed = apply_suppression_rules(ALERTS, RULES)
    ids = {a["id"] for a in suppressed}
    assert "a3" in ids  # plc-01 in MW-002 wildcard
    assert "a4" in ids  # rtu-05 in MW-002 wildcard


def test_suppressed_event_has_rule_id():
    _, suppressed = apply_suppression_rules(ALERTS, RULES)
    a1 = next(a for a in suppressed if a["id"] == "a1")
    assert a1["suppressed_by"] == "MW-001"


def test_boundary_timestamps_inclusive():
    alerts = [
        {"id": "start", "device_id": "plc-01", "ts": 1000},  # exactly at start
        {"id": "end",   "device_id": "plc-01", "ts": 2000},  # exactly at end
    ]
    _, suppressed = apply_suppression_rules(alerts, RULES)
    ids = {a["id"] for a in suppressed}
    assert "start" in ids and "end" in ids


def test_empty_alerts():
    passed, suppressed = apply_suppression_rules([], RULES)
    assert passed == [] and suppressed == []


def test_no_rules_all_pass():
    passed, suppressed = apply_suppression_rules(ALERTS, [])
    assert len(passed) == len(ALERTS) and suppressed == []


if __name__ == "__main__":
    test_alert_in_maintenance_window_suppressed()
    test_alert_outside_window_passed()
    test_wrong_device_not_suppressed()
    test_wildcard_rule_suppresses_all_devices()
    test_suppressed_event_has_rule_id()
    test_boundary_timestamps_inclusive()
    test_empty_alerts()
    test_no_rules_all_pass()
    print("All tests passed.")
