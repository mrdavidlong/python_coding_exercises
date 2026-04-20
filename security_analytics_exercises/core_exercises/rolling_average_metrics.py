"""
Problem: Compute a rolling (moving) average over the last N readings for each
device's sensor values. Useful for smoothing noisy OT sensor data.

How the sliding window with deque works:
---------------------------------------------------------------------------

  values = [10, 20, 30, 40, 50],  window = 3

  deque(maxlen=3) automatically evicts the leftmost item when it fills up.
  We maintain a running_sum in parallel to avoid re-summing each step.

  Step 1:  buf=[10]        sum=10          avg = 10/1 = 10.0
  Step 2:  buf=[10,20]     sum=30          avg = 30/2 = 15.0
  Step 3:  buf=[10,20,30]  sum=60  ← FULL  avg = 60/3 = 20.0
  Step 4:  buf=[20,30,40]  evict 10        avg = 90/3 = 30.0
           (deque auto-evicts buf[0]=10; we subtract it from sum before append)
  Step 5:  buf=[30,40,50]  evict 20        avg = 120/3 = 40.0

  Why maintain running_sum instead of sum(buf)?
    sum(buf) is O(window) per step → O(n*window) total.
    running_sum gives O(1) per step → O(n) total.
    For large windows or high-frequency OT sensors this matters.

  Why deque(maxlen=N) instead of a plain list with slicing?
    deque append/popleft are O(1). List slicing (list[-N:]) creates a new
    object and is O(N). deque also makes the "full?" check trivial: len==maxlen.

Example input:
    readings = [10, 20, 30, 40, 50]
    window = 3

Expected rolling averages: [10.0, 15.0, 20.0, 30.0, 40.0]
"""

from collections import defaultdict, deque
from typing import Any


def rolling_average(values: list[float], window: int) -> list[float]:
    """Compute a rolling average over the last N values at each position.

    Partial windows at the start use fewer than `window` values (no padding).

    Args:
        values: Ordered list of sensor readings.  e.g. [10, 20, 30, 40, 50]
        window: Number of values to average.      e.g. 3

    Returns:
        List of averages, same length as values.
        e.g. [10.0, 15.0, 20.0, 30.0, 40.0]
             (first two are partial: [10]/1, [10,20]/2; then full windows of 3)

    Raises:
        ValueError if window <= 0.
    """
    if window <= 0:
        raise ValueError("window must be positive")

    buf: deque[float] = deque(maxlen=window)  # oldest item auto-evicted when full
    running_sum = 0.0
    result      = []

    for v in values:
        # Before appending, check if the deque is full.
        # If so, buf[0] is about to be evicted by deque — subtract it from the sum first.
        if len(buf) == window:
            running_sum -= buf[0]    # buf[0] is the value that will be pushed out
        buf.append(v) # when .append() happens, original buf[0] is pushed out, i.e. buf[1] becomes buf[0]
        running_sum += v

        # Divide by actual buffer length (handles partial window at start)
        result.append(round(running_sum / len(buf), 6))

    return result


def rolling_average_by_device(
    readings: list[dict[str, Any]],
    window: int,
    value_field: str = "value",
) -> list[dict[str, Any]]:
    """Compute a rolling average per device across an interleaved reading stream.

    Each device maintains its OWN independent deque and running sum so that
    readings from device B don't pollute device A's rolling window.

    Args:
        readings:    List of reading dicts with "device_id" and a numeric value field.
                     e.g. [{"device_id":"d1","value":10.0,"ts":1},
                            {"device_id":"d2","value":100.0,"ts":1},
                            {"device_id":"d1","value":20.0,"ts":2}]
        window:      Rolling window size per device.  e.g. 2
        value_field: Key holding the numeric reading.  Defaults to "value".

    Returns:
        Same list in the same order, each dict enriched with "rolling_avg".
        e.g. [{"device_id":"d1","value":10.0,"ts":1,"rolling_avg":10.0},
               {"device_id":"d2","value":100.0,"ts":1,"rolling_avg":100.0},
               {"device_id":"d1","value":20.0,"ts":2,"rolling_avg":15.0}]
    """
    # defaultdict(lambda) captures `window` so each new device gets its own
    # deque with the right maxlen. defaultdict(float) gives 0.0 for new devices.
    # Both eliminate the manual "if device_id not in" initialisation guard.
    # device_bufs e.g. {"plc-01": deque([10.0, 20.0, 30.0], maxlen=3), "rtu-05": deque([100.0], maxlen=3)}
    # device_sums e.g. {"plc-01": 60.0, "rtu-05": 100.0}
    # defaultdict calls this factory with no args, so lambda must take no params.
    # Each missing device_id gets a fresh deque(maxlen=window) instead of sharing one.
    device_bufs: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=window))
    device_sums: dict[str, float]        = defaultdict(float)
    result = []

    for reading in readings:
        device_id = reading["device_id"]
        value     = reading[value_field]

        buf = device_bufs[device_id]  # auto-creates deque(maxlen=window) on first access

        # Subtract the about-to-be-evicted value before deque evicts it
        if len(buf) == window:
            device_sums[device_id] -= buf[0]
        buf.append(value)
        device_sums[device_id] += value

        avg = round(device_sums[device_id] / len(buf), 6)
        result.append({**reading, "rolling_avg": avg})

    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_basic_rolling_average():
    result = rolling_average([10, 20, 30, 40, 50], window=3)
    assert result[0] == 10.0   # partial: [10]
    assert result[1] == 15.0   # partial: [10, 20]
    assert result[2] == 20.0   # full:    [10, 20, 30]
    assert result[3] == 30.0   # full:    [20, 30, 40]  (10 evicted)
    assert result[4] == 40.0   # full:    [30, 40, 50]  (20 evicted)


def test_window_1_equals_identity():
    values = [5.0, 3.0, 8.0]
    assert rolling_average(values, window=1) == values


def test_window_larger_than_input():
    # Window never fills → all readings are partial
    result = rolling_average([1, 2, 3], window=10)
    assert result[2] == 2.0  # mean of [1, 2, 3]


def test_empty_input():
    assert rolling_average([], window=3) == []


def test_invalid_window_raises():
    try:
        rolling_average([1, 2, 3], window=0)
        assert False
    except ValueError:
        pass


def test_per_device_rolling():
    readings = [
        {"device_id": "d1", "value": 10.0, "ts": 1},
        {"device_id": "d1", "value": 20.0, "ts": 2},
        {"device_id": "d2", "value": 100.0, "ts": 1},  # separate device — own window
        {"device_id": "d1", "value": 30.0, "ts": 3},
    ]
    result = rolling_average_by_device(readings, window=2)
    d1_avgs = [r["rolling_avg"] for r in result if r["device_id"] == "d1"]
    # d1: [10] → 10.0, [10,20] → 15.0, [20,30] → 25.0
    # d2 interleaved but doesn't affect d1's window
    assert d1_avgs == [10.0, 15.0, 25.0]


if __name__ == "__main__":
    test_basic_rolling_average()
    test_window_1_equals_identity()
    test_window_larger_than_input()
    test_empty_input()
    test_invalid_window_raises()
    test_per_device_rolling()
    print("All tests passed.")
