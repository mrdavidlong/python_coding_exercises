"""
Problem: Given a time-ordered list of sensor readings for a device, fire an alert
whenever a reading exceeds the threshold for N or more consecutive readings.
Return the start index and count of each violation run.

How consecutive-run detection works:
---------------------------------------------------------------------------

  readings = [10, 20, 95, 98, 91, 15, 99, 100]   threshold=90, consecutive=2

  idx:  0    1    2    3    4    5    6    7
  val: [10] [20] [95] [98] [91] [15] [99] [100]
        ok   ok   ↑    ↑    ↑   ok   ↑    ↑
                  └── run1 ──┘        └─ run2 ─┘
                  start=2, len=3       start=6, len=2
                  ✓ (≥ 2)              ✓ (≥ 2)

  State machine per reading:
    value > threshold → extend current run (or start one)
    value ≤ threshold → close run; emit if len ≥ consecutive; reset state

  Edge case — run reaching the END of the list:
    The closing "≤ threshold" reading never comes, so we emit after the loop.

  Threshold is EXCLUSIVE: value must be strictly GREATER than threshold.
  A reading equal to the threshold does NOT count as a violation.

Example input:
    readings = [10, 20, 95, 98, 91, 15, 99, 100]
    threshold = 90, consecutive = 2

Expected output:
    [
        {"start_index": 2, "count": 3, "values": [95, 98, 91]},  # indices 2-4
        {"start_index": 6, "count": 2, "values": [99, 100]},     # indices 6-7
    ]
"""

from typing import Any


def find_threshold_violations(
    readings: list[float],
    threshold: float,
    consecutive: int = 3,
) -> list[dict[str, Any]]:
    """Find runs where a sensor reading exceeds threshold for N or more consecutive steps.

    Args:
        readings:    Ordered list of sensor values.
                     e.g. [10.0, 85.0, 90.0, 95.0, 5.0, 88.0, 92.0, 91.0]
        threshold:   Value that must be strictly exceeded to count.  e.g. 80.0
        consecutive: Minimum run length to report.  e.g. 3

    Returns:
        List of violation dicts, one per qualifying run:
          "start_index": index of the first exceeding value in readings
          "count":       length of the run
          "values":      copy of the readings in that run
        e.g. [{"start_index":1,"count":3,"values":[85.0,90.0,95.0]},
               {"start_index":5,"count":3,"values":[88.0,92.0,91.0]}]
        Returns [] if no run is long enough.
    """
    violations  = []
    run_start   = None          # index where the current run began (None = no active run)
    run_values: list[float] = []  # values collected in the current run

    for i, value in enumerate(readings):
        if value > threshold:
            # Start a new run on first exceeding value
            if run_start is None:
                run_start = i
            run_values.append(value)
        else:
            # This reading breaks the run — check if the run was long enough to report
            if run_start is not None and len(run_values) >= consecutive:
                violations.append({
                    "start_index": run_start,
                    "count":       len(run_values),
                    "values":      list(run_values),  # copy so later mutations don't affect result
                })
            # Reset run state regardless of whether we reported it
            run_start  = None
            run_values = []

    # A run that reaches the end of the list is never closed by a "below threshold"
    # reading inside the loop, so we must check and emit it here.
    if run_start is not None and len(run_values) >= consecutive:
        violations.append({
            "start_index": run_start,
            "count":       len(run_values),
            "values":      list(run_values),
        })

    return violations


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_basic_two_violations():
    readings = [10, 20, 95, 98, 91, 15, 99, 100]
    result = find_threshold_violations(readings, threshold=90, consecutive=2)
    assert len(result) == 2
    assert result[0]["start_index"] == 2
    assert result[0]["count"] == 3
    assert result[1]["start_index"] == 6
    assert result[1]["count"] == 2


def test_run_too_short_not_reported():
    # Only 1 consecutive reading over threshold; minimum is 2
    readings = [10, 95, 10, 10]
    result = find_threshold_violations(readings, threshold=90, consecutive=2)
    assert result == []


def test_run_at_end_of_list():
    # The run extends to the final index — relies on the post-loop emit
    readings = [10, 10, 95, 98, 99]
    result = find_threshold_violations(readings, threshold=90, consecutive=3)
    assert len(result) == 1
    assert result[0]["start_index"] == 2


def test_no_violations():
    readings = [10, 20, 30, 40]
    assert find_threshold_violations(readings, threshold=90, consecutive=1) == []


def test_entire_list_is_one_violation():
    readings = [95, 96, 97, 98]
    result = find_threshold_violations(readings, threshold=90, consecutive=2)
    assert len(result) == 1
    assert result[0]["count"] == 4


def test_exactly_at_threshold_not_triggered():
    # Threshold is exclusive: value must be STRICTLY greater
    readings = [90, 90, 90]
    assert find_threshold_violations(readings, threshold=90, consecutive=1) == []


def test_empty_input():
    assert find_threshold_violations([], threshold=90, consecutive=2) == []


if __name__ == "__main__":
    test_basic_two_violations()
    test_run_too_short_not_reported()
    test_run_at_end_of_list()
    test_no_violations()
    test_entire_list_is_one_violation()
    test_exactly_at_threshold_not_triggered()
    test_empty_input()
    print("All tests passed.")
