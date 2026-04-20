"""
Question

You are given alerts from different tools:

asset_id
technique
source
timestamp

Treat alerts as duplicates if they have the same asset_id and technique and occur within 15 minutes. Return merged alerts with:

distinct sources
earliest timestamp
latest timestamp
count of merged alerts

What this tests
Grouping, sorting, interval merge logic, and clean stateful coding.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

def merge_alerts(alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Merge duplicate alerts by asset and technique within a 15-minute window.

    Args:
        alerts: list[dict]
            Each alert should include:
            - asset_id
            - technique
            - source
            - timestamp: ISO-8601 timestamp string

    Returns:
        list[dict]:
            Merged clusters with:
            - asset_id
            - technique
            - start
            - end
            - sources
            - count

    Example:
        merge_alerts([
            {"asset_id": "a1", "technique": "t1", "source": "s1", "timestamp": "2025-02-01T10:00:00"},
            {"asset_id": "a1", "technique": "t1", "source": "s2", "timestamp": "2025-02-01T10:10:00"},
        ])
        # [{"asset_id": "a1", "technique": "t1", "count": 2, ...}]
    """
    # Example key/value:
    # ("asset1", "tech1") -> [{"asset_id": "asset1", "technique": "tech1", "source": "source1", ...}, ...]
    grouped: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    # Group alerts by the duplicate key before building time clusters.
    for a in alerts:
        key = (a["asset_id"], a["technique"])
        row = dict(a)
        row["dt"] = datetime.fromisoformat(a["timestamp"])
        grouped[key].append(row)

    # Example merged row:
    # {"asset_id": "asset1", "technique": "tech1", "start": "...", "end": "...", "sources": ["source1"], "count": 1}
    merged: list[dict[str, Any]] = []

    for (asset_id, technique), rows in grouped.items():
        rows.sort(key=lambda x: x["dt"])
        if not rows:
            continue

        # Seed the first cluster from the earliest row for this group.
        # Example current cluster:
        # {"asset_id": "asset1", "technique": "tech1", "sources": {"source1", "source2"}, "count": 2, ...}
        current: dict[str, Any] = {
            "asset_id": asset_id,
            "technique": technique,
            "start": rows[0]["timestamp"],
            "end": rows[0]["timestamp"],
            "sources": {rows[0]["source"]},
            "count": 1,
            "last_dt": rows[0]["dt"],
        }

        for row in rows[1:]:
            if row["dt"] - current["last_dt"] <= timedelta(minutes=15):
                # This alert extends the active cluster.
                current["end"] = row["timestamp"]
                current["sources"].add(row["source"])
                current["count"] += 1
                current["last_dt"] = row["dt"]
            else:
                # Close the cluster and start a new one after a time gap.
                merged.append({
                    "asset_id": current["asset_id"],
                    "technique": current["technique"],
                    "start": current["start"],
                    "end": current["end"],
                    "sources": sorted(current["sources"]),
                    "count": current["count"],
                })
                current = {
                    "asset_id": asset_id,
                    "technique": technique,
                    "start": row["timestamp"],
                    "end": row["timestamp"],
                    "sources": {row["source"]},
                    "count": 1,
                    "last_dt": row["dt"],
                }

        if current:
            # Flush the final cluster for this group.
            merged.append({
                "asset_id": current["asset_id"],
                "technique": current["technique"],
                "start": current["start"],
                "end": current["end"],
                "sources": sorted(current["sources"]),
                "count": current["count"],
            })

    return merged


def test_no_alerts() -> None:
    result = merge_alerts([])
    # Empty input should remain empty.
    assert result == []


def test_single_alert() -> None:
    alerts = [{
        "asset_id": "asset1",
        "technique": "tech1",
        "source": "source1",
        "timestamp": "2025-02-01T10:00:00",
    }]
    result = merge_alerts(alerts)
    # One alert becomes one cluster with count 1.
    assert len(result) == 1
    assert result[0]["asset_id"] == "asset1"
    assert result[0]["count"] == 1
    assert result[0]["sources"] == ["source1"]


def test_alerts_different_asset_ids() -> None:
    alerts = [
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source1",
            "timestamp": "2025-02-01T10:00:00",
        },
        {
            "asset_id": "asset2",
            "technique": "tech1",
            "source": "source1",
            "timestamp": "2025-02-01T10:00:00",
        },
    ]
    result = merge_alerts(alerts)
    # Different asset IDs are never merged together.
    assert len(result) == 2


def test_alerts_different_techniques() -> None:
    alerts = [
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source1",
            "timestamp": "2025-02-01T10:00:00",
        },
        {
            "asset_id": "asset1",
            "technique": "tech2",
            "source": "source1",
            "timestamp": "2025-02-01T10:00:00",
        },
    ]
    result = merge_alerts(alerts)
    # Different techniques also stay in separate clusters.
    assert len(result) == 2


def test_merge_within_15_minutes() -> None:
    alerts = [
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source1",
            "timestamp": "2025-02-01T10:00:00",
        },
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source2",
            "timestamp": "2025-02-01T10:10:00",
        },
    ]
    result = merge_alerts(alerts)
    # The second alert lands inside the 15-minute window, so they merge.
    assert len(result) == 1
    assert result[0]["count"] == 2
    assert sorted(result[0]["sources"]) == ["source1", "source2"]


def test_no_merge_outside_15_minutes() -> None:
    alerts = [
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source1",
            "timestamp": "2025-02-01T10:00:00",
        },
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source2",
            "timestamp": "2025-02-01T10:16:00",
        },
    ]
    result = merge_alerts(alerts)
    # A 16-minute gap breaks the cluster into two outputs.
    assert len(result) == 2


def test_multiple_merges() -> None:
    alerts = [
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source1",
            "timestamp": "2025-02-01T10:00:00",
        },
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source2",
            "timestamp": "2025-02-01T10:10:00",
        },
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source3",
            "timestamp": "2025-02-01T10:20:00",
        },
    ]
    result = merge_alerts(alerts)
    # Each alert arrives within 15 minutes of the previous one, so they chain together.
    assert len(result) == 1
    assert result[0]["count"] == 3


def test_timestamp_order_preserved() -> None:
    alerts = [
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source1",
            "timestamp": "2025-02-01T10:10:00",
        },
        {
            "asset_id": "asset1",
            "technique": "tech1",
            "source": "source2",
            "timestamp": "2025-02-01T10:00:00",
        },
    ]
    result = merge_alerts(alerts)
    # The earliest timestamp should become the cluster start.
    assert result[0]["start"] == "2025-02-01T10:00:00"
    assert result[0]["end"] == "2025-02-01T10:10:00"


if __name__ == "__main__":
    test_no_alerts()
    test_single_alert()
    test_alerts_different_asset_ids()
    test_alerts_different_techniques()
    test_merge_within_15_minutes()
    test_no_merge_outside_15_minutes()
    test_multiple_merges()
    test_timestamp_order_preserved()
    print("All tests passed.")
