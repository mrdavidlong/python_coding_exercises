"""
Problem: Before ingesting a batch of device telemetry events, run data quality
checks to catch bad data early. Return a quality report with counts and offending
record IDs.

Checks to perform:
  1. Missing required fields (device_id, ts, value)
  2. Null / None values in non-nullable fields
  3. Out-of-range values (value must be between min_value and max_value if provided)
  4. Duplicate event IDs within the batch

Report format:
    {
        "total":              int,
        "passed":             int,
        "failed":             int,
        "missing_fields":     [{"id": ..., "missing": [field, ...]}],
        "null_values":        [{"id": ..., "fields": [field, ...]}],
        "out_of_range":       [{"id": ..., "field": ..., "value": ...}],
        "duplicate_ids":      [id, ...],
    }
"""

from __future__ import annotations

from collections import Counter
from typing import Any

REQUIRED_FIELDS     = ["id", "device_id", "ts", "value"]
NON_NULLABLE_FIELDS = ["device_id", "ts", "value"]


def run_quality_checks(
    events: list[dict[str, Any]],
    min_value: float | None = None,
    max_value: float | None = None,
) -> dict[str, Any]:
    """Scan a batch of events for data quality issues: missing fields, nulls, range violations, duplicates.

    Args:
        events:     List of event dicts. Expected keys: "id", "ts", "device_id", "value".
                    e.g. [{"id":"e1","ts":1000,"device_id":"plc-01","value":45.0},
                           {"id":"e2","ts":None,"device_id":"rtu-05","value":200.0}]
        min_value:  Inclusive lower bound for "value". None = no lower check.  e.g. 0.0
        max_value:  Inclusive upper bound for "value". None = no upper check.  e.g. 100.0

    Returns:
        Dict with keys:
          "total_events":    int — total input count
          "failed_count":    int — events failing at least one check
          "missing_fields":  list of {"id", "missing": [field_names]}
          "null_values":     list of {"id", "field", "value": None}
          "out_of_range":    list of {"id", "field", "value"}
          "duplicate_ids":   list of duplicate "id" values
        e.g. {"total_events":2,"failed_count":1,
               "null_values":[{"id":"e2","field":"ts","value":None}],
               "out_of_range":[{"id":"e2","field":"value","value":200.0}], ...}
    """
    # e.g. missing_fields: [{"id": "e1", "missing": ["severity", "ts"]}]
    # e.g. null_values:    [{"id": "e2", "field": "value", "value": None}]
    # e.g. out_of_range:   [{"id": "e3", "field": "cpu_pct", "value": 150.0}]
    # e.g. failed_ids:     {"e1", "e2", "e3"}  — union of all events that failed any check
    missing_fields: list[dict]  = []
    null_values:    list[dict]  = []
    out_of_range:   list[dict]  = []
    failed_ids:     set[str]    = set()

    id_counts = Counter(e.get("id") for e in events if e.get("id") is not None)
    duplicate_ids = [eid for eid, cnt in id_counts.items() if cnt > 1]

    for event in events:
        event_id = event.get("id", "<no-id>")

        # Check for missing required fields
        missing = [f for f in REQUIRED_FIELDS if f not in event]
        if missing:
            missing_fields.append({"id": event_id, "missing": missing})
            failed_ids.add(event_id)

        # Check for null values in non-nullable fields
        nulls = [f for f in NON_NULLABLE_FIELDS if f in event and event[f] is None]
        if nulls:
            null_values.append({"id": event_id, "fields": nulls})
            failed_ids.add(event_id)

        # Check value range if the field is present and non-null
        value = event.get("value")
        if value is not None:
            if min_value is not None and value < min_value:
                out_of_range.append({"id": event_id, "field": "value", "value": value})
                failed_ids.add(event_id)
            elif max_value is not None and value > max_value:
                out_of_range.append({"id": event_id, "field": "value", "value": value})
                failed_ids.add(event_id)

    # Duplicate IDs also count as failures
    for eid in duplicate_ids:
        failed_ids.add(eid)

    total  = len(events)
    failed = len(failed_ids)

    return {
        "total":          total,
        "passed":         total - failed,
        "failed":         failed,
        "missing_fields": missing_fields,
        "null_values":    null_values,
        "out_of_range":   out_of_range,
        "duplicate_ids":  duplicate_ids,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

CLEAN_EVENTS = [
    {"id": "e1", "device_id": "plc-01", "ts": 1000, "value": 45.0},
    {"id": "e2", "device_id": "rtu-05", "ts": 1001, "value": 30.0},
]


def test_clean_batch_passes():
    report = run_quality_checks(CLEAN_EVENTS)
    assert report["total"] == 2
    assert report["failed"] == 0
    assert report["missing_fields"] == []


def test_missing_field_detected():
    events = [{"id": "e1", "device_id": "plc-01", "ts": 1000}]  # missing 'value'
    report = run_quality_checks(events)
    assert report["failed"] == 1
    assert any("value" in r["missing"] for r in report["missing_fields"])


def test_null_value_detected():
    events = [{"id": "e1", "device_id": "plc-01", "ts": 1000, "value": None}]
    report = run_quality_checks(events)
    assert report["failed"] == 1
    assert any("value" in r["fields"] for r in report["null_values"])


def test_out_of_range_detected():
    events = [{"id": "e1", "device_id": "d1", "ts": 1, "value": 150.0}]
    report = run_quality_checks(events, min_value=0, max_value=100)
    assert len(report["out_of_range"]) == 1
    assert report["out_of_range"][0]["id"] == "e1"


def test_duplicate_ids_detected():
    events = [
        {"id": "e1", "device_id": "d1", "ts": 1, "value": 1.0},
        {"id": "e1", "device_id": "d2", "ts": 2, "value": 2.0},  # duplicate id
    ]
    report = run_quality_checks(events)
    assert "e1" in report["duplicate_ids"]


def test_empty_batch():
    report = run_quality_checks([])
    assert report["total"] == 0 and report["failed"] == 0


if __name__ == "__main__":
    test_clean_batch_passes()
    test_missing_field_detected()
    test_null_value_detected()
    test_out_of_range_detected()
    test_duplicate_ids_detected()
    test_empty_batch()
    print("All tests passed.")
