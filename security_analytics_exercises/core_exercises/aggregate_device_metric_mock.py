from collections import defaultdict
from statistics import mean
from typing import Any

def aggregate_device_metrics(readings: list[dict[str, Any]]
) -> dict[str, dict[str, dict[str, float]]]:
    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in readings:
        key = (r["device_id"], r["metric"])
        buckets[key].append(r["value"])
    
    result: dict[str, dict[str, dict[str, float]]] = {}
    for (device_id, metric), values in buckets.items():
        if device_id not in result:
            result[device_id] = {}
        result[device_id][metric] = {
            "min": min(values),
            "max": max(values),
            "avg": round(mean(values), 4),
            "count": len(values)
        }
    return result






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

if __name__ == "__main__":
    test_basic_aggregation()