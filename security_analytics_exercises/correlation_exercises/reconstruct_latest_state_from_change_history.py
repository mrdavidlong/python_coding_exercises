"""
Reconstruct latest state from change history

Question

You are given change events for findings:

finding_id
timestamp
status in ["open", "investigating", "resolved"]
owner

Return the latest state per finding, keeping only the latest event by timestamp.

Common follow up
“What if there are ties?”
You answer: define tie-breaking explicitly, for example:
- stable input order: keep the first event seen for the same timestamp
- status priority: resolved > investigating > open
- owner priority: prefer a specific owner rule, such as latest owner alphabetically
"""

from datetime import datetime
from typing import Any


def latest_finding_state(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Keep the latest event for each finding.

    Args:
        events: list[dict]
            Each event should include:
            - finding_id
            - timestamp: ISO-8601 timestamp string
            - status
            - owner

    Returns:
        dict[str, dict]:
            Mapping of finding_id to the latest event row.

    Example:
        latest_finding_state([
            {"finding_id": "f1", "timestamp": "2025-02-01T10:00:00", "status": "open", "owner": "owner1"},
            {"finding_id": "f1", "timestamp": "2025-02-01T10:10:00", "status": "resolved", "owner": "owner2"},
        ])
        # {"f1": {"finding_id": "f1", "timestamp": "2025-02-01T10:10:00", ...}}
    """
    return latest_finding_state_stable(events)


def latest_finding_state_stable(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Keep the latest event per finding using stable input order on ties.

    If two events have the same timestamp, the first one seen wins.
    """
    # Example key/value:
    # "finding1" -> {"finding_id": "finding1", "timestamp": "2025-02-01T10:10:00", ...}
    latest: dict[str, dict[str, Any]] = {}

    for e in events:
        fid: str = e["finding_id"]
        ts: datetime = datetime.fromisoformat(e["timestamp"])

        # Replace only when the new event is strictly newer.
        if fid not in latest or ts > datetime.fromisoformat(latest[fid]["timestamp"]):
            latest[fid] = e

    return latest


def latest_finding_state_status_priority(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Keep the latest event per finding, breaking timestamp ties by status priority.

    Priority order:
    resolved > investigating > open
    """
    status_rank: dict[str, int] = {
        "open": 1,
        "investigating": 2,
        "resolved": 3,
    }
    latest: dict[str, dict[str, Any]] = {}

    for e in events:
        fid: str = e["finding_id"]
        ts: datetime = datetime.fromisoformat(e["timestamp"])

        if fid not in latest:
            latest[fid] = e
            continue

        current_ts: datetime = datetime.fromisoformat(latest[fid]["timestamp"])
        if ts > current_ts:
            latest[fid] = e
            continue

        if ts == current_ts and status_rank[e["status"]] > status_rank[latest[fid]["status"]]:
            # Prefer the event with the more final status when timestamps tie.
            latest[fid] = e

    return latest


def latest_finding_state_owner_priority(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Keep the latest event per finding, breaking timestamp ties by owner name.

    Tie-break rule:
    - if timestamps are equal, prefer the owner that comes first alphabetically
    """
    latest: dict[str, dict[str, Any]] = {}

    for e in events:
        fid: str = e["finding_id"]
        ts: datetime = datetime.fromisoformat(e["timestamp"])

        if fid not in latest:
            latest[fid] = e
            continue

        current_ts: datetime = datetime.fromisoformat(latest[fid]["timestamp"])
        if ts > current_ts:
            latest[fid] = e
            continue

        if ts == current_ts and e["owner"] < latest[fid]["owner"]:
            # Alphabetically smaller owner wins on a timestamp tie.
            latest[fid] = e

    return latest


def test_no_events() -> None:
    result = latest_finding_state([])
    # No events means no state to reconstruct.
    assert result == {}


def test_single_event() -> None:
    events = [{
        "finding_id": "finding1",
        "timestamp": "2025-02-01T10:00:00",
        "status": "open",
        "owner": "owner1",
    }]
    result = latest_finding_state(events)
    # One event becomes one entry in the result map.
    assert len(result) == 1
    assert result["finding1"]["status"] == "open"


def test_multiple_findings() -> None:
    events = [
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:00:00",
            "status": "open",
            "owner": "owner1",
        },
        {
            "finding_id": "finding2",
            "timestamp": "2025-02-01T10:01:00",
            "status": "resolved",
            "owner": "owner2",
        },
    ]
    result = latest_finding_state(events)
    # Two finding IDs should produce two latest-state rows.
    assert len(result) == 2


def test_latest_event_selected() -> None:
    events = [
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:00:00",
            "status": "open",
            "owner": "owner1",
        },
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:10:00",
            "status": "investigating",
            "owner": "owner2",
        },
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:05:00",
            "status": "resolved",
            "owner": "owner3",
        },
    ]
    result = latest_finding_state(events)
    # The 10:10 event is newer than 10:05 and 10:00, so it wins.
    assert result["finding1"]["status"] == "investigating"
    assert result["finding1"]["owner"] == "owner2"


def test_unordered_events() -> None:
    events = [
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:10:00",
            "status": "resolved",
            "owner": "owner3",
        },
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:00:00",
            "status": "open",
            "owner": "owner1",
        },
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:05:00",
            "status": "investigating",
            "owner": "owner2",
        },
    ]
    result = latest_finding_state(events)
    # Sorting is not required because the newest timestamp still wins.
    assert result["finding1"]["status"] == "resolved"


def test_stable_tie_breaker_keeps_first_seen() -> None:
    events = [
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:00:00",
            "status": "open",
            "owner": "owner1",
        },
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:00:00",
            "status": "resolved",
            "owner": "owner2",
        },
    ]
    result = latest_finding_state_stable(events)
    # Stable input order keeps the first event when timestamps match.
    assert result["finding1"]["status"] == "open"
    assert result["finding1"]["owner"] == "owner1"


def test_status_priority_tie_breaker() -> None:
    events = [
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:00:00",
            "status": "open",
            "owner": "owner1",
        },
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:00:00",
            "status": "resolved",
            "owner": "owner2",
        },
    ]
    result = latest_finding_state_status_priority(events)
    # Resolved outranks open when timestamps tie.
    assert result["finding1"]["status"] == "resolved"
    assert result["finding1"]["owner"] == "owner2"


def test_owner_priority_tie_breaker() -> None:
    events = [
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:00:00",
            "status": "investigating",
            "owner": "ownerz",
        },
        {
            "finding_id": "finding1",
            "timestamp": "2025-02-01T10:00:00",
            "status": "investigating",
            "owner": "ownera",
        },
    ]
    result = latest_finding_state_owner_priority(events)
    # Alphabetically smaller owner wins on equal timestamps.
    assert result["finding1"]["owner"] == "ownera"


if __name__ == "__main__":
    test_no_events()
    test_single_event()
    test_multiple_findings()
    test_latest_event_selected()
    test_unordered_events()
    test_stable_tie_breaker_keeps_first_seen()
    test_status_priority_tie_breaker()
    test_owner_priority_tie_breaker()
    print("All tests passed.")
