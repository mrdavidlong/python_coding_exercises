"""
Problem: Bucket a list of timestamped events into fixed time slots (hourly or daily)
and count events per slot. Useful for spotting attack patterns that spike at certain
times (e.g., off-hours activity in an OT environment).

Return a dict mapping slot_label → count, sorted chronologically.

Example input:
    events = [
        {"id": "e1", "ts": 1700010000},  # 2023-11-14 22:xx UTC
        {"id": "e2", "ts": 1700010600},  # same hour
        {"id": "e3", "ts": 1700014000},  # next hour
    ]
    bucket_events(events, bucket="hour")

Expected output:
    {"2023-11-14T22:00Z": 2, "2023-11-14T23:00Z": 1}
"""

from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any


def _floor_to_hour(dt: datetime) -> datetime:
    """Truncate a datetime to the start of its hour."""
    return dt.replace(minute=0, second=0, microsecond=0)


def _floor_to_day(dt: datetime) -> datetime:
    """Truncate a datetime to midnight of its day."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def bucket_events(
    events: list[dict[str, Any]],
    bucket: str = "hour",
    ts_field: str = "ts",
) -> dict[str, int]:
    """Count events per hourly or daily time slot.

    Args:
        events:   List of event dicts, each with a Unix epoch timestamp.
                  e.g. [{"id":"e1","ts":1699999200},{"id":"e2","ts":1699999800}]
        bucket:   Granularity: "hour" (floor to the hour) or "day" (floor to midnight).
                  e.g. "hour"
        ts_field: Key holding the timestamp in each dict.  Defaults to "ts".

    Returns:
        Dict mapping ISO-formatted slot string → event count, sorted by slot ascending.
        "hour" format: "2023-11-14T22:00Z"
        "day"  format: "2023-11-14"
        e.g. {"2023-11-14T22:00Z": 2, "2023-11-14T23:00Z": 1}

    Raises:
        ValueError if bucket is not "hour" or "day".
    """
    if bucket not in ("hour", "day"):
        raise ValueError(f"bucket must be 'hour' or 'day', got {bucket!r}")

    floor_fn   = _floor_to_hour if bucket == "hour" else _floor_to_day
    fmt        = "%Y-%m-%dT%H:%MZ" if bucket == "hour" else "%Y-%m-%d"

    # e.g. {datetime(2023,11,14,22,0, tzinfo=utc): 3, datetime(2023,11,14,23,0, tzinfo=utc): 1}
    counts: dict[datetime, int] = defaultdict(int)
    for event in events:
        dt    = datetime.fromtimestamp(event[ts_field], tz=timezone.utc)
        slot  = floor_fn(dt)
        counts[slot] += 1

    return {slot.strftime(fmt): count for slot, count in sorted(counts.items())}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# 1700000000 = 2023-11-14 22:13:20 UTC, so 22:00:00 UTC = 1699999200
EVENTS = [
    {"id": "e1", "ts": 1699999200},  # 2023-11-14 22:00:00 UTC
    {"id": "e2", "ts": 1699999800},  # 2023-11-14 22:10:00 UTC (same hour)
    {"id": "e3", "ts": 1700003160},  # 2023-11-14 23:06:00 UTC (next hour)
    {"id": "e4", "ts": 1700085600},  # 2023-11-15 22:00:00 UTC (next day)
]


def test_hourly_buckets():
    result = bucket_events(EVENTS, bucket="hour")
    assert result.get("2023-11-14T22:00Z") == 2
    assert result.get("2023-11-14T23:00Z") == 1


def test_daily_buckets():
    result = bucket_events(EVENTS, bucket="day")
    assert result.get("2023-11-14") == 3
    assert result.get("2023-11-15") == 1


def test_sorted_chronologically():
    result = bucket_events(EVENTS, bucket="hour")
    keys = list(result.keys())
    assert keys == sorted(keys)


def test_empty_input():
    assert bucket_events([], bucket="hour") == {}


def test_invalid_bucket_raises():
    try:
        bucket_events(EVENTS, bucket="minute")
        assert False
    except ValueError:
        pass


def test_single_event():
    events = [{"id": "e1", "ts": 1699999200}]  # 2023-11-14 22:00 UTC
    result = bucket_events(events, bucket="day")
    assert result == {"2023-11-14": 1}


if __name__ == "__main__":
    test_hourly_buckets()
    test_daily_buckets()
    test_sorted_chronologically()
    test_empty_input()
    test_invalid_bucket_raises()
    test_single_event()
    print("All tests passed.")
