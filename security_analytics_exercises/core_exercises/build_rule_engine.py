"""
Problem: Build a simple rule engine that loads alert rules from a config list
and evaluates each incoming event against all rules. Return the list of rules
that matched, along with the action to take.

Rule format:
    {
        "rule_id":   "R001",
        "field":     "alert_type",         # event field to check
        "operator":  "eq" | "neq" | "in" | "not_in" | "gt" | "lt" | "contains",
        "value":     "cmd_inject",         # comparison value
        "action":    "page_oncall",        # what to do on match
        "priority":  1,                    # lower = more important
    }

Example:
    rules = [
        {"rule_id": "R001", "field": "severity",   "operator": "eq",  "value": "CRITICAL", "action": "page_oncall",    "priority": 1},
        {"rule_id": "R002", "field": "alert_type", "operator": "in",  "value": ["cmd_inject", "safety_override"], "action": "isolate_device", "priority": 1},
        {"rule_id": "R003", "field": "source",     "operator": "eq",  "value": "external",  "action": "block_ip",       "priority": 2},
    ]
    event = {"severity": "CRITICAL", "alert_type": "cmd_inject", "source": "external"}
    → matches R001, R002, R003 → all three actions
"""

from typing import Any


def evaluate_rule(rule: dict[str, Any], event: dict[str, Any]) -> bool:
    """Test whether a single rule matches an event.

    Each operator compares event.get(field) against rule["value"].
    Missing event fields return False for gt/lt, and treat the field as ""
    for contains — never raises TypeError or AttributeError.

    Args:
        rule:  Rule dict with keys: "field" (str), "operator" (str), "value" (Any).
               Supported operators: "eq","neq","in","not_in","gt","lt","contains"
               e.g. {"field":"severity","operator":"eq","value":"CRITICAL"}
        event: The event to test against.
               e.g. {"severity":"CRITICAL","alert_type":"cmd_inject","count":5}

    Returns:
        True if the rule matches, False otherwise.
        e.g. evaluate_rule({"field":"severity","operator":"eq","value":"CRITICAL"},
                            {"severity":"CRITICAL"}) → True

    Raises:
        ValueError if operator is not one of the supported values.
    """
    field    = rule["field"]
    operator = rule["operator"]
    expected = rule["value"]
    actual   = event.get(field)   # None if the field doesn't exist on this event

    if operator == "eq":
        return actual == expected
    if operator == "neq":
        return actual != expected
    if operator == "in":
        # "actual is a member of the expected collection"
        return actual in expected
    if operator == "not_in":
        return actual not in expected
    if operator == "gt":
        # Guard: skip comparison if field is absent to avoid TypeError
        return actual is not None and actual > expected
    if operator == "lt":
        return actual is not None and actual < expected
    if operator == "contains":
        # "expected substring appears in the actual string field"
        return expected in (actual or "")   # (actual or "") handles None gracefully

    raise ValueError(f"Unknown operator: {operator!r}")


def run_rules(
    event: dict[str, Any],
    rules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Evaluate all rules against an event and return matching rules sorted by priority.

    Args:
        event: The event to evaluate.
               e.g. {"severity":"CRITICAL","alert_type":"cmd_inject","source":"external"}
        rules: List of rule dicts, each with "field","operator","value","action","priority".
               e.g. [{"rule_id":"R001","field":"severity","operator":"eq",
                       "value":"CRITICAL","action":"page_oncall","priority":1}]

    Returns:
        List of matching rule dicts sorted ascending by "priority" (lower = more urgent).
        e.g. [{"rule_id":"R001","priority":1,...}, {"rule_id":"R003","priority":2,...}]
        Empty list if no rules match.
    """
    matched = [r for r in rules if evaluate_rule(r, event)]
    return sorted(matched, key=lambda r: r.get("priority", 999))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

RULES = [
    {"rule_id": "R001", "field": "severity",   "operator": "eq",     "value": "CRITICAL",                        "action": "page_oncall",    "priority": 1},
    {"rule_id": "R002", "field": "alert_type", "operator": "in",     "value": ["cmd_inject", "safety_override"],  "action": "isolate_device", "priority": 1},
    {"rule_id": "R003", "field": "source",     "operator": "eq",     "value": "external",                        "action": "block_ip",       "priority": 2},
    {"rule_id": "R004", "field": "count",      "operator": "gt",     "value": 10,                                "action": "throttle",       "priority": 3},
    {"rule_id": "R005", "field": "message",    "operator": "contains","value": "overflow",                        "action": "alert_eng",      "priority": 2},
]


def test_eq_operator():
    event = {"severity": "CRITICAL", "alert_type": "heartbeat", "source": "internal"}
    matched = run_rules(event, RULES)
    assert any(r["rule_id"] == "R001" for r in matched)
    assert not any(r["rule_id"] == "R003" for r in matched)


def test_in_operator():
    event = {"severity": "HIGH", "alert_type": "cmd_inject", "source": "internal"}
    matched = run_rules(event, RULES)
    assert any(r["rule_id"] == "R002" for r in matched)


def test_gt_operator():
    event = {"severity": "LOW", "alert_type": "scan", "source": "internal", "count": 15}
    matched = run_rules(event, RULES)
    assert any(r["rule_id"] == "R004" for r in matched)


def test_contains_operator():
    event = {"severity": "LOW", "message": "stack overflow detected", "source": "internal"}
    matched = run_rules(event, RULES)
    assert any(r["rule_id"] == "R005" for r in matched)


def test_no_match():
    event = {"severity": "INFO", "alert_type": "heartbeat", "source": "internal"}
    assert run_rules(event, RULES) == []


def test_multiple_matches_sorted_by_priority():
    event = {"severity": "CRITICAL", "alert_type": "cmd_inject", "source": "external", "count": 5}
    matched = run_rules(event, RULES)
    priorities = [r["priority"] for r in matched]
    assert priorities == sorted(priorities)


def test_unknown_operator_raises():
    rule  = {"rule_id": "BAD", "field": "x", "operator": "startswith", "value": "foo", "action": "noop", "priority": 1}
    event = {"x": "foobar"}
    try:
        evaluate_rule(rule, event)
        assert False, "Should have raised"
    except ValueError:
        pass


if __name__ == "__main__":
    test_eq_operator()
    test_in_operator()
    test_gt_operator()
    test_contains_operator()
    test_no_match()
    test_multiple_matches_sorted_by_priority()
    test_unknown_operator_raises()
    print("All tests passed.")
