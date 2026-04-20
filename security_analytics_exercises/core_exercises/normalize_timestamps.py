"""
Problem: Events arrive from heterogeneous sources with different timestamp formats.
Normalize all timestamps to UTC-aware datetime objects.

Supported input formats:
  - int/float  → Unix epoch seconds (e.g. 1700000000)
  - str ISO 8601 with timezone  → "2023-11-14T22:13:20+00:00"
  - str ISO 8601 without timezone → "2023-11-14T22:13:20"  (assume UTC)
  - str date only → "2023-11-14"  (assume midnight UTC)

Example input:
    timestamps = [1700000000, "2023-11-14T22:13:20+00:00", "2023-11-14T22:13:20", "2023-11-14"]

Expected output:
    All four become datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)
    (the date-only becomes midnight: datetime(2023, 11, 14, 0, 0, 0, tzinfo=timezone.utc))
"""

from __future__ import annotations

from datetime import datetime, timezone


def normalize_timestamp(ts: int | float | str) -> datetime:
    """Convert a timestamp in any supported format to a UTC-aware datetime.

    Format detection strategy:
      - int/float → epoch seconds (fastest path, no parsing needed)
      - str       → try each format in order; first match wins.

    Format order matters: "%Y-%m-%dT%H:%M:%S%z" must come BEFORE
    "%Y-%m-%dT%H:%M:%S" because strptime with %z can parse strings that
    also match the no-tz format, but not vice versa.

    replace(tzinfo=UTC) is used (not astimezone) because we're ASSERTING
    the string is UTC when no tz is specified — not converting from some
    other timezone.

    Args:
        ts: Timestamp in any of these forms:
              int/float — epoch seconds:        e.g. 1700000000
              str ISO with tz  — with offset:   e.g. "2023-11-14T22:13:20+00:00"
              str ISO no tz    — assumed UTC:   e.g. "2023-11-14T22:13:20"
              str date only    — assumed UTC:   e.g. "2023-11-14"

    Returns:
        UTC-aware datetime object.
        e.g. datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)

    Raises:
        ValueError: if ts is not int/float/str or no format matches.
    """
    if isinstance(ts, (int, float)):
        # fromtimestamp with tz=utc interprets the number as UTC epoch seconds
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    if isinstance(ts, str):
        # Try formats from most specific to least specific
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(ts, fmt)
                # strptime only fills tzinfo when the format includes %z;
                # for tz-naive strings, we attach UTC explicitly
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue   # try the next format

    raise ValueError(f"Unsupported timestamp format: {ts!r}")


def normalize_event_timestamps(
    events: list[dict],
    ts_field: str = "ts",
) -> list[dict]:
    """Apply normalize_timestamp to one field across a list of event dicts.

    Args:
        events:   List of event dicts.
                  e.g. [{"id":"e1","ts":1700000000}, {"id":"e2","ts":"2023-11-14T22:13:20"}]
        ts_field: The key to normalize in each dict. Defaults to "ts".

    Returns:
        New list of dicts (originals not mutated) with ts_field replaced by datetime.
        e.g. [{"id":"e1","ts":datetime(2023,11,14,22,13,20,tzinfo=utc)}, ...]
    """
    result = []
    for event in events:
        updated = dict(event) # same as event.copy()
        if ts_field in updated:
            updated[ts_field] = normalize_timestamp(updated[ts_field])
        result.append(updated)
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

EPOCH = 1700000000
EXPECTED_DT = datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)


def test_epoch_int():
    result = normalize_timestamp(EPOCH)
    assert result == EXPECTED_DT


def test_epoch_float():
    result = normalize_timestamp(float(EPOCH))
    assert result == EXPECTED_DT


def test_iso_with_tz():
    result = normalize_timestamp("2023-11-14T22:13:20+00:00")
    assert result == EXPECTED_DT


def test_iso_without_tz():
    result = normalize_timestamp("2023-11-14T22:13:20")
    assert result == EXPECTED_DT


def test_date_only():
    result = normalize_timestamp("2023-11-14")
    assert result == datetime(2023, 11, 14, 0, 0, 0, tzinfo=timezone.utc)


def test_result_is_utc_aware():
    for ts in [EPOCH, "2023-11-14T22:13:20", "2023-11-14T22:13:20+00:00"]:
        result = normalize_timestamp(ts)
        assert result.tzinfo is not None


def test_normalize_event_list():
    events = [{"id": "e1", "ts": EPOCH}, {"id": "e2", "ts": "2023-11-14T22:13:20"}]
    result = normalize_event_timestamps(events)
    assert all(isinstance(e["ts"], datetime) for e in result)


def test_unsupported_format_raises():
    try:
        normalize_timestamp("not-a-date")
        assert False, "Should have raised"
    except ValueError:
        pass


if __name__ == "__main__":
    test_epoch_int()
    test_epoch_float()
    test_iso_with_tz()
    test_iso_without_tz()
    test_date_only()
    test_result_is_utc_aware()
    test_normalize_event_list()
    test_unsupported_format_raises()
    print("All tests passed.")
