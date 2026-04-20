"""
Question

You are given events with:

asset_id
timestamp
source
technique
severity

Create a finding for an asset if it has events from at least 2 distinct sources within a 30 minute window. For each finding, return:

asset_id
earliest timestamp in the triggering window
latest timestamp in the triggering window
set of sources
set of techniques
highest severity in the window


Why this is likely
It tests grouping, sorting, sliding window, and business logic in one problem.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

SEVERITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def correlate_findings(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Build findings from correlated events inside a 30-minute window.

    Args:
        events: list[dict]
            Each event should include:
            - asset_id
            - timestamp: ISO-8601 timestamp string
            - source
            - technique
            - severity

    Returns:
        list[dict]:
            One finding per asset when at least 2 distinct sources appear
            inside a 30-minute sliding window.

    Example:
        correlate_findings([
            {"asset_id": "a1", "timestamp": "2025-02-01T10:00:00", "source": "s1", "technique": "t1", "severity": "high"},
            {"asset_id": "a1", "timestamp": "2025-02-01T10:10:00", "source": "s2", "technique": "t1", "severity": "medium"},
        ])
        # [{"asset_id": "a1", "start": "2025-02-01T10:00:00", ...}]
    """
    # Example key/value:
    # "asset1" -> [{"asset_id": "asset1", "source": "source1", "severity": "high", ...}, ...]
    by_asset: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    for e in events:
        row = dict(e)
        row["dt"] = parse_ts(e["timestamp"])
        by_asset[e["asset_id"]].append(row)

    # Example finding row:
    # {"asset_id": "asset1", "start": "...", "end": "...", "sources": ["source1", "source2"], ...}
    findings: list[dict[str, Any]] = []

    for asset_id, rows in by_asset.items():
        rows.sort(key=lambda x: x["dt"])

        left: int = 0
        for right in range(len(rows)):
            # Shrink the window until it fits inside 30 minutes.
            while rows[right]["dt"] - rows[left]["dt"] > timedelta(minutes=30):
                left += 1

            # Example window: the slice covering the last 30 minutes of rows for one asset.
            window: list[dict[str, Any]] = rows[left:right + 1]
            # Use a set so repeated source values in the window are deduped.
            # Example sources: {"source1", "source2"}; the set removes duplicates.
            sources: set[str] = {r["source"] for r in window}

            if len(sources) >= 2:
                # Once the first qualifying window is found, emit one finding and stop.
                highest: str = max(window, key=lambda r: SEVERITY_RANK[r["severity"]])["severity"]
                findings.append({
                    "asset_id": asset_id,
                    "start": window[0]["timestamp"],
                    "end": window[-1]["timestamp"],
                    "sources": sorted(sources),
                    "techniques": sorted({r["technique"] for r in window}),
                    "highest_severity": highest,
                })
                break

    return findings


def test_no_events() -> None:
    result = correlate_findings([])
    # Without events there is no correlated finding.
    assert result == []


def test_single_event() -> None:
    events = [{
        "asset_id": "asset1",
        "timestamp": "2025-02-01T10:00:00",
        "source": "source1",
        "technique": "tech1",
        "severity": "high",
    }]
    result = correlate_findings(events)
    # One source alone cannot produce a finding.
    assert result == []


def test_two_sources_within_window() -> None:
    events = [
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:00:00",
            "source": "source1",
            "technique": "tech1",
            "severity": "high",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:10:00",
            "source": "source2",
            "technique": "tech1",
            "severity": "medium",
        },
    ]
    result = correlate_findings(events)
    # Two distinct sources within 10 minutes satisfy the correlation rule.
    assert len(result) == 1
    assert result[0]["asset_id"] == "asset1"
    assert result[0]["start"] == "2025-02-01T10:00:00"
    assert result[0]["end"] == "2025-02-01T10:10:00"
    assert sorted(result[0]["sources"]) == ["source1", "source2"]


def test_two_sources_outside_window() -> None:
    events = [
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:00:00",
            "source": "source1",
            "technique": "tech1",
            "severity": "high",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:31:00",
            "source": "source2",
            "technique": "tech1",
            "severity": "medium",
        },
    ]
    result = correlate_findings(events)
    # The second event is 31 minutes later, so the window never qualifies.
    assert result == []


def test_multiple_events_same_source() -> None:
    events = [
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:00:00",
            "source": "source1",
            "technique": "tech1",
            "severity": "high",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:10:00",
            "source": "source1",
            "technique": "tech1",
            "severity": "medium",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:20:00",
            "source": "source2",
            "technique": "tech1",
            "severity": "low",
        },
    ]
    result = correlate_findings(events)
    # Same-source repeats do not satisfy the distinct-source threshold by themselves.
    assert len(result) == 1


def test_multiple_assets() -> None:
    events = [
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:00:00",
            "source": "source1",
            "technique": "tech1",
            "severity": "high",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:10:00",
            "source": "source2",
            "technique": "tech1",
            "severity": "high",
        },
        {
            "asset_id": "asset2",
            "timestamp": "2025-02-01T10:00:00",
            "source": "source1",
            "technique": "tech2",
            "severity": "medium",
        },
        {
            "asset_id": "asset2",
            "timestamp": "2025-02-01T10:10:00",
            "source": "source2",
            "technique": "tech2",
            "severity": "medium",
        },
    ]
    result = correlate_findings(events)
    # Each asset is evaluated independently, so this produces two findings.
    assert len(result) == 2


def test_highest_severity_selected() -> None:
    events = [
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:00:00",
            "source": "source1",
            "technique": "tech1",
            "severity": "low",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:10:00",
            "source": "source2",
            "technique": "tech1",
            "severity": "critical",
        },
    ]
    result = correlate_findings(events)
    # The highest severity in the window should be preserved in the finding.
    assert result[0]["highest_severity"] == "critical"


def test_multiple_techniques_aggregated() -> None:
    events = [
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:00:00",
            "source": "source1",
            "technique": "tech1",
            "severity": "high",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:10:00",
            "source": "source2",
            "technique": "tech2",
            "severity": "high",
        },
    ]
    result = correlate_findings(events)
    # Techniques are collected from the whole triggering window.
    assert sorted(result[0]["techniques"]) == ["tech1", "tech2"]


def test_exactly_30_minute_boundary() -> None:
    events = [
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:00:00",
            "source": "source1",
            "technique": "tech1",
            "severity": "high",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:30:00",
            "source": "source2",
            "technique": "tech1",
            "severity": "high",
        },
    ]
    result = correlate_findings(events)
    # Exactly 30 minutes is still inside the allowed window.
    assert len(result) == 1


def test_first_matching_window_found() -> None:
    events = [
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:00:00",
            "source": "source1",
            "technique": "tech1",
            "severity": "high",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:10:00",
            "source": "source2",
            "technique": "tech1",
            "severity": "high",
        },
        {
            "asset_id": "asset1",
            "timestamp": "2025-02-01T10:20:00",
            "source": "source3",
            "technique": "tech1",
            "severity": "high",
        },
    ]
    result = correlate_findings(events)
    # The first qualifying window should be returned, not a later wider one.
    assert len(result) == 1
    assert result[0]["sources"] == ["source1", "source2"]


if __name__ == "__main__":
    test_no_events()
    test_single_event()
    test_two_sources_within_window()
    test_two_sources_outside_window()
    test_multiple_events_same_source()
    test_multiple_assets()
    test_highest_severity_selected()
    test_multiple_techniques_aggregated()
    test_exactly_30_minute_boundary()
    test_first_matching_window_found()
    print("All tests passed.")
