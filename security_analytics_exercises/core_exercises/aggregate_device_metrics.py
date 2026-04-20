"""
Problem: Given a list of metric reading dicts, compute min/max/avg/count
per device per metric name.

Example input:
    readings = [
        {"device_id": "plc-01", "metric": "cpu_pct",  "value": 45.0},
        {"device_id": "plc-01", "metric": "cpu_pct",  "value": 60.0},
        {"device_id": "plc-01", "metric": "mem_mb",   "value": 512.0},
        {"device_id": "plc-02", "metric": "cpu_pct",  "value": 30.0},
    ]

Expected output:
    {
        "plc-01": {
            "cpu_pct": {"min": 45.0, "max": 60.0, "avg": 52.5, "count": 2},
            "mem_mb":  {"min": 512.0, "max": 512.0, "avg": 512.0, "count": 1},
        },
        "plc-02": {
            "cpu_pct": {"min": 30.0, "max": 30.0, "avg": 30.0, "count": 1},
        },
    }
"""

from collections import defaultdict
from statistics import mean
from typing import Any


def aggregate_device_metrics(
    readings: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, float]]]:
    """Group metric readings by device and compute min/max/avg/count per metric.

    Two-pass approach:
      Pass 1 — collect all raw values into buckets keyed by (device_id, metric).
      Pass 2 — compute stats over each bucket.

    We accumulate first instead of computing stats incrementally because
    statistics.mean() is more numerically stable than a running sum.

    Args:
        readings: List of reading dicts, each with:
                    "device_id" (str)   — e.g. "plc-01"
                    "metric"    (str)   — e.g. "cpu_pct"
                    "value"     (float) — e.g. 45.0
                  e.g. [{"device_id":"plc-01","metric":"cpu_pct","value":45.0},
                         {"device_id":"plc-01","metric":"cpu_pct","value":60.0}]

    Returns:
        Nested dict: device_id → metric → {"min","max","avg","count"}.
        e.g. {"plc-01": {"cpu_pct": {"min":45.0,"max":60.0,"avg":52.5,"count":2}}}
    """
    # Pass 1: bucket raw values — defaultdict(list) auto-creates an empty list
    # for any new (device_id, metric) key we haven't seen before.
    # e.g. {("plc-01", "cpu_pct"): [45.0, 60.0], ("plc-01", "mem_mb"): [512.0]}
    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in readings:
        key = (r["device_id"], r["metric"])
        buckets[key].append(r["value"])

    # Pass 2: compute stats and build the nested output dict.
    # defaultdict(dict) auto-creates an empty {} for any new device_id,
    # so we don't need an explicit "if device_id not in result" guard.
    # e.g. {"plc-01": {"cpu_pct": {"min": 45.0, ...}, "mem_mb": {...}}, "plc-02": {...}}
    result: dict[str, dict] = defaultdict(dict)
    for (device_id, metric), values in buckets.items(): #remember to add .items()
        result[device_id][metric] = {
            "min":   min(values),
            "max":   max(values),
            "avg":   round(mean(values), 4),
            "count": len(values), #remember len() is count
        }
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SAMPLE_READINGS = [
    {"device_id": "plc-01", "metric": "cpu_pct", "value": 45.0},
    {"device_id": "plc-01", "metric": "cpu_pct", "value": 60.0},
    {"device_id": "plc-01", "metric": "mem_mb",  "value": 512.0},
    {"device_id": "plc-02", "metric": "cpu_pct", "value": 30.0},
]


def test_basic_aggregation():
    result = aggregate_device_metrics(SAMPLE_READINGS)
    plc01_cpu = result["plc-01"]["cpu_pct"]
    assert plc01_cpu["min"] == 45.0
    assert plc01_cpu["max"] == 60.0
    assert plc01_cpu["avg"] == 52.5
    assert plc01_cpu["count"] == 2


def test_single_reading_stats():
    result = aggregate_device_metrics(SAMPLE_READINGS)
    plc02_cpu = result["plc-02"]["cpu_pct"]
    assert plc02_cpu["min"] == plc02_cpu["max"] == plc02_cpu["avg"] == 30.0


def test_multiple_metrics_per_device():
    result = aggregate_device_metrics(SAMPLE_READINGS)
    assert set(result["plc-01"].keys()) == {"cpu_pct", "mem_mb"}


def test_empty_input():
    assert aggregate_device_metrics([]) == {}


def test_single_reading():
    result = aggregate_device_metrics([{"device_id": "d1", "metric": "temp", "value": 99.5}])
    assert result["d1"]["temp"]["avg"] == 99.5


if __name__ == "__main__":
    test_basic_aggregation()
    test_single_reading_stats()
    test_multiple_metrics_per_device()
    test_empty_input()
    test_single_reading()
    print("All tests passed.")
