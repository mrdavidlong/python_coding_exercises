"""
Problem: Parse a CSV incident report (as a string), compute summary statistics,
and flag rows where the duration_minutes is an outlier (> mean + 2 * std_dev).

CSV format:
    incident_id,device_id,severity,duration_minutes
    INC-001,plc-01,HIGH,45
    INC-002,rtu-05,MEDIUM,12
    ...

Return a dict with:
    - "total": total incident count
    - "by_severity": {severity: count}
    - "avg_duration": float
    - "outliers": list of incident_id strings for unusually long incidents
"""

import csv
import io
import statistics
from collections import defaultdict
from typing import Any


def parse_incident_csv(csv_text: str) -> dict[str, Any]:
    """Parse a CSV incident report and compute summary stats with outlier detection.

    Outliers are rows where duration_minutes > mean + 2 * stdev (2-sigma rule).
    Requires at least 2 rows to compute stdev; single-row input has no outliers.

    Args:
        csv_text: CSV string with header row.
                  Required columns: incident_id, device_id, severity, duration_minutes
                  e.g. "incident_id,device_id,severity,duration_minutes\\n
                         INC-001,plc-01,HIGH,45\\nINC-002,rtu-05,MEDIUM,12\\n"

    Returns:
        Dict with keys:
          "total":        total number of incidents (int)
          "by_severity":  count per severity level  e.g. {"HIGH":1,"MEDIUM":1}
          "avg_duration": mean duration in minutes (float, rounded to 2dp)
          "outliers":     list of incident_id strings with unusually long duration
        e.g. {"total":2,"by_severity":{"HIGH":1,"MEDIUM":1},"avg_duration":28.5,"outliers":[]}
    """
    reader   = csv.DictReader(io.StringIO(csv_text.strip()))
    rows     = list(reader)

    if not rows:
        return {"total": 0, "by_severity": {}, "avg_duration": 0.0, "outliers": []}

    durations: list[float] = [float(r["duration_minutes"]) for r in rows]

    # defaultdict(int) is correct here: the default value (0) is uniform for
    # every key — a classic counter accumulator. No sentinel, no custom default.
    # Plain dict would need: by_severity.get(sev, 0) + 1 — extra noise for no benefit.
    by_severity: dict[str, int] = defaultdict(int)
    for r in rows:
        by_severity[r["severity"]] += 1

    avg = statistics.mean(durations)

    # Need at least 2 data points for std dev
    if len(durations) >= 2:
        std  = statistics.stdev(durations)
        threshold = avg + 2 * std
        
        # The zip() function in Python is a built-in utility that aggregates elements from two or more iterables (such as lists, tuples, or strings) into a single iterator of tuples. 
        # names = ["Alice", "Bob"]
        # scores = [85, 90]
        # result = zip(names, scores)
        # print(list(result)) # Output: [('Alice', 85), ('Bob', 90)]
        outlier_ids = [
            r["incident_id"] for r, d in zip(rows, durations) if d > threshold
        ]
    else:
        outlier_ids = []

    return {
        "total":        len(rows),
        "by_severity":  by_severity,
        "avg_duration": round(avg, 2),
        "outliers":     outlier_ids,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SAMPLE_CSV = """incident_id,device_id,severity,duration_minutes
INC-001,plc-01,HIGH,45
INC-002,rtu-05,MEDIUM,12
INC-003,hmi-03,HIGH,50
INC-004,plc-02,LOW,8
INC-005,plc-01,MEDIUM,11
INC-006,rtu-05,HIGH,200
"""


def test_total_count():
    result = parse_incident_csv(SAMPLE_CSV)
    assert result["total"] == 6


def test_severity_counts():
    result = parse_incident_csv(SAMPLE_CSV)
    assert result["by_severity"]["HIGH"] == 3
    assert result["by_severity"]["MEDIUM"] == 2
    assert result["by_severity"]["LOW"] == 1


def test_avg_duration():
    result = parse_incident_csv(SAMPLE_CSV)
    expected_avg = round((45 + 12 + 50 + 8 + 11 + 200) / 6, 2)
    assert result["avg_duration"] == expected_avg


def test_outlier_detected():
    # Use a dataset where the outlier is unambiguously > mean + 2*stdev
    csv_clear = """incident_id,device_id,severity,duration_minutes
INC-A,d1,HIGH,10
INC-B,d1,HIGH,12
INC-C,d1,HIGH,11
INC-D,d1,HIGH,10
INC-E,d1,HIGH,13
INC-F,d1,HIGH,500
"""
    result = parse_incident_csv(csv_clear)
    assert "INC-F" in result["outliers"]
    for normal in ["INC-A", "INC-B", "INC-C", "INC-D", "INC-E"]:
        assert normal not in result["outliers"]


def test_empty_csv():
    result = parse_incident_csv("incident_id,device_id,severity,duration_minutes\n")
    assert result["total"] == 0
    assert result["outliers"] == []


def test_single_row_no_outlier():
    csv_text = "incident_id,device_id,severity,duration_minutes\nINC-001,d1,HIGH,30\n"
    result = parse_incident_csv(csv_text)
    assert result["outliers"] == []  # can't compute std dev with 1 row


if __name__ == "__main__":
    test_total_count()
    test_severity_counts()
    test_avg_duration()
    test_outlier_detected()
    test_empty_csv()
    test_single_row_no_outlier()
    print("All tests passed.")
