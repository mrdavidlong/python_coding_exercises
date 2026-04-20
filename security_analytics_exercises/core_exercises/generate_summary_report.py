"""
Problem: After an incident investigation, generate a human-readable summary
report from a list of raw events. The report should aggregate key facts an
analyst needs at a glance.

Report fields:
    - incident_window:  {"start": min_ts, "end": max_ts}
    - total_events:     int
    - affected_devices: sorted list of unique device IDs
    - severity_counts:  {severity: count}
    - top_alert_types:  top 3 alert types by frequency
    - timeline:         list of {"ts": ..., "device_id": ..., "summary": ...}
                        sorted by ts, one entry per event
"""

from collections import Counter
from typing import Any


def generate_summary_report(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate a flat list of events into a human-readable incident summary.

    Args:
        events: List of event dicts, each with keys:
                  "ts"         (float) — epoch seconds (required for timeline/window)
                  "device_id"  (str)   — optional
                  "severity"   (str)   — optional, e.g. "CRITICAL"
                  "alert_type" (str)   — optional, e.g. "cmd_inject"
                e.g. [{"ts":1000,"device_id":"plc-01","severity":"HIGH","alert_type":"scan"},
                       {"ts":1200,"device_id":"rtu-05","severity":"CRITICAL","alert_type":"cmd_inject"}]

    Returns:
        Summary dict with keys:
          "incident_window":  {"start": float, "end": float} or None if no events
          "total_events":     int
          "affected_devices": sorted list of unique device_ids
          "severity_counts":  {"HIGH":1,"CRITICAL":1,...}
          "top_alert_types":  top-3 alert_type strings by frequency
          "timeline":         list of {"ts","device_id","summary"} sorted by ts
        e.g. {"incident_window":{"start":1000,"end":1200},
               "total_events":2,
               "affected_devices":["plc-01","rtu-05"],
               "severity_counts":{"HIGH":1,"CRITICAL":1},
               "top_alert_types":["cmd_inject","scan"],
               "timeline":[{"ts":1000,"device_id":"plc-01","summary":"scan [HIGH]"}, ...]}
    """
    if not events:
        return {
            "incident_window":  None,
            "total_events":     0,
            "affected_devices": [],
            "severity_counts":  {},
            "top_alert_types":  [],
            "timeline":         [],
        }

    sorted_events = sorted(events, key=lambda e: e["ts"])

    severity_counts = Counter(e.get("severity", "UNKNOWN") for e in events)
    alert_type_counts = Counter(e.get("alert_type", "unknown") for e in events)

    timeline = [
        {
            "ts":        e["ts"],
            "device_id": e.get("device_id", "unknown"),
            # One-line human summary combining alert type and severity
            "summary":   f"{e.get('alert_type', 'event')} [{e.get('severity', '?')}]",
        }
        for e in sorted_events
    ]

    return {
        "incident_window":  {"start": sorted_events[0]["ts"], "end": sorted_events[-1]["ts"]},
        "total_events":     len(events),
        "affected_devices": sorted({e.get("device_id") for e in events if e.get("device_id")}),
        "severity_counts":  dict(severity_counts),
        "top_alert_types":  [t for t, _ in alert_type_counts.most_common(3)],
        "timeline":         timeline,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SAMPLE_EVENTS = [
    {"device_id": "plc-01", "alert_type": "port_scan",    "severity": "MEDIUM", "ts": 1000},
    {"device_id": "plc-01", "alert_type": "cmd_inject",   "severity": "CRITICAL","ts": 1100},
    {"device_id": "rtu-05", "alert_type": "port_scan",    "severity": "MEDIUM", "ts": 1050},
    {"device_id": "rtu-05", "alert_type": "auth_failure", "severity": "HIGH",   "ts": 1200},
    {"device_id": "plc-01", "alert_type": "port_scan",    "severity": "MEDIUM", "ts": 1300},
]


def test_incident_window():
    report = generate_summary_report(SAMPLE_EVENTS)
    assert report["incident_window"]["start"] == 1000
    assert report["incident_window"]["end"]   == 1300


def test_total_events():
    report = generate_summary_report(SAMPLE_EVENTS)
    assert report["total_events"] == 5


def test_affected_devices_sorted():
    report = generate_summary_report(SAMPLE_EVENTS)
    assert report["affected_devices"] == ["plc-01", "rtu-05"]


def test_severity_counts():
    report = generate_summary_report(SAMPLE_EVENTS)
    assert report["severity_counts"]["MEDIUM"]   == 3
    assert report["severity_counts"]["CRITICAL"] == 1
    assert report["severity_counts"]["HIGH"]     == 1


def test_top_alert_types():
    report = generate_summary_report(SAMPLE_EVENTS)
    # port_scan appears 3 times — should be #1
    assert report["top_alert_types"][0] == "port_scan"
    assert len(report["top_alert_types"]) <= 3


def test_timeline_sorted_by_ts():
    report = generate_summary_report(SAMPLE_EVENTS)
    tss = [e["ts"] for e in report["timeline"]]
    assert tss == sorted(tss)


def test_empty_events():
    report = generate_summary_report([])
    assert report["total_events"] == 0
    assert report["incident_window"] is None


if __name__ == "__main__":
    test_incident_window()
    test_total_events()
    test_affected_devices_sorted()
    test_severity_counts()
    test_top_alert_types()
    test_timeline_sorted_by_ts()
    test_empty_events()
    print("All tests passed.")
