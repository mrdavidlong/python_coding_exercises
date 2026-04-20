"""
Question

Given login events with:

user_id
timestamp
success

Return all users who have 3 or more failed logins in any 10 minute window.

What this tests
Basic sliding window, sorting, and careful boundary logic.

"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

def flagged_users(events: list[dict[str, Any]]) -> list[str]:
    """
    Return users who have at least 3 failed logins in any 10-minute window.

    Args:
        events: list[dict]
            Each event should include:
            - user_id
            - timestamp: ISO-8601 timestamp string
            - success: boolean login result

    Returns:
        list[str]:
            Sorted user IDs that meet the threshold.

    Example:
        flagged_users([
            {"user_id": "u1", "timestamp": "2025-02-01T10:00:00", "success": False},
            {"user_id": "u1", "timestamp": "2025-02-01T10:05:00", "success": False},
            {"user_id": "u1", "timestamp": "2025-02-01T10:09:00", "success": False},
        ])
        # ["u1"]
    """
    # Example key/value:
    # "user1" -> [datetime(2025, 2, 1, 10, 0), datetime(2025, 2, 1, 10, 5)]
    failures: defaultdict[str, list[datetime]] = defaultdict(list)

    # Keep only failed attempts and group them by user.
    for e in events:
        if not e["success"]:
            failures[e["user_id"]].append(datetime.fromisoformat(e["timestamp"]))

    # Example contents: ["user1", "user7"]
    result: list[str] = []

    for user_id, times in failures.items():
        # Example sorted list: [10:00, 10:05, 10:09]
        times.sort()
        left: int = 0

        # Slide a 10-minute window across the sorted failure timestamps.
        for right in range(len(times)):
            while times[right] - times[left] > timedelta(minutes=10):
                left += 1

            if right - left + 1 >= 3:
                # The user qualifies as soon as one window hits three failures.
                result.append(user_id)
                break

    return sorted(result)

def test_no_events() -> None:
    result = flagged_users([])
    # No events means nobody can be flagged.
    assert result == []


def test_all_successful_logins() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": True},
        {"user_id": "user1", "timestamp": "2025-02-01T10:01:00", "success": True},
    ]
    result = flagged_users(events)
    # Successful logins are ignored, so there are no failures to count.
    assert result == []


def test_less_than_three_failures() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:01:00", "success": False},
    ]
    result = flagged_users(events)
    # Only two failures is below the threshold of three.
    assert result == []


def test_three_failures_within_10_minutes() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:05:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:09:00", "success": False},
    ]
    result = flagged_users(events)
    # Three failures within 9 minutes satisfies the rule.
    assert result == ["user1"]


def test_three_failures_outside_10_minute_window() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:05:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:11:00", "success": False},
    ]
    result = flagged_users(events)
    # The third failure is 11 minutes after the first, so the window is too wide.
    assert result == []


def test_multiple_users_flagged() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:05:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:09:00", "success": False},
        {"user_id": "user2", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user2", "timestamp": "2025-02-01T10:05:00", "success": False},
        {"user_id": "user2", "timestamp": "2025-02-01T10:09:00", "success": False},
    ]
    result = flagged_users(events)
    # Each user independently hits the threshold.
    assert result == ["user1", "user2"]


def test_mixed_successes_and_failures() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": True},
        {"user_id": "user1", "timestamp": "2025-02-01T10:01:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:05:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:09:00", "success": False},
    ]
    result = flagged_users(events)
    # Failures still count even when a success appears between them.
    assert result == ["user1"]


def test_exactly_10_minute_boundary() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:05:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:10:00", "success": False},
    ]
    result = flagged_users(events)
    # 10:00, 10:05, and 10:10 fit inside one inclusive 10-minute window.
    assert result == ["user1"]


def test_unsorted_input() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:09:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:05:00", "success": False},
    ]
    result = flagged_users(events)
    # Sorting inside the function should make unsorted input still qualify.
    assert result == ["user1"]


def test_duplicate_timestamps_count_separately() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
    ]
    result = flagged_users(events)
    # Three failed attempts at the same time still count as three failures.
    assert result == ["user1"]


def test_multiple_users_only_one_flags() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:03:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:07:00", "success": False},
        {"user_id": "user2", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user2", "timestamp": "2025-02-01T10:20:00", "success": False},
        {"user_id": "user2", "timestamp": "2025-02-01T10:40:00", "success": False},
    ]
    result = flagged_users(events)
    # Only user1 has three failures within one 10-minute window.
    assert result == ["user1"]


def test_late_failure_does_not_extend_window() -> None:
    events = [
        {"user_id": "user1", "timestamp": "2025-02-01T10:00:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:04:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:09:00", "success": False},
        {"user_id": "user1", "timestamp": "2025-02-01T10:11:00", "success": False},
    ]
    result = flagged_users(events)
    # The first three failures already qualify; the later one should not change the result.
    assert result == ["user1"]


if __name__ == "__main__":
    test_no_events()
    test_all_successful_logins()
    test_less_than_three_failures()
    test_three_failures_within_10_minutes()
    test_three_failures_outside_10_minute_window()
    test_multiple_users_flagged()
    test_mixed_successes_and_failures()
    test_exactly_10_minute_boundary()
    test_unsorted_input()
    test_duplicate_timestamps_count_separately()
    test_multiple_users_only_one_flags()
    test_late_failure_does_not_extend_window()
    print("All tests passed.")
