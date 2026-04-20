"""
Problem: An alert pipeline fires too many duplicate alerts during an incident.
Implement a stateful rate limiter that suppresses repeat alerts for the same
(device_id, alert_type) key within a cooldown window.

How per-key cooldown suppression works:
---------------------------------------------------------------------------

  cooldown = 60s
  key = ("plc-01", "auth_failure")

  ts=1000  process() → key not in _last_forwarded → FORWARD, record ts=1000
  ts=1045  process() → 1045 - 1000 = 45s  ≤ 60 → SUPPRESS
  ts=1060  process() → 1060 - 1000 = 60s  ≤ 60 → SUPPRESS  (boundary exclusive)
  ts=1061  process() → 1061 - 1000 = 61s  > 60 → FORWARD,  record ts=1061
  ts=1090  process() → 1090 - 1061 = 29s  ≤ 60 → SUPPRESS

  Timeline:
  1000   1045   1060   1061         1090
  [FWD]--[SUPP]-[SUPP]-[FWD]--------[SUPP]
         45s    60s    61s→reset    29s from 1061

  Key insight: the cooldown window resets from each FORWARDED alert's ts,
  not from the original alert's ts. So a long burst that finally breaks
  through starts a fresh cooldown from the moment it was forwarded.

  Each (device_id, alert_type) pair has its OWN independent cooldown.
  Noise from plc-01 auth_failure does not affect plc-01 cmd_inject.

The limiter is a class that processes alerts one at a time (as a stream).
Call process(alert) → True if the alert should be forwarded, False if suppressed.

Example:
    limiter = AlertRateLimiter(cooldown_seconds=60)
    limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000}) → True
    limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1045}) → False (within 60s)
    limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1065}) → True  (cooldown expired)
"""

from __future__ import annotations

from typing import Any


class AlertRateLimiter:
    """Stateful per-(device, alert_type) cooldown suppressor."""

    def __init__(self, cooldown_seconds: int = 60) -> None:
        self.cooldown_seconds = cooldown_seconds
        # Plain dict (not defaultdict): a missing key means "never forwarded before".
        # .get(key) returning None is the sentinel that triggers an unconditional forward.
        # defaultdict(float) → 0.0 would look like epoch time (Jan 1 1970), not "never".
        # e.g. {("plc-01", "auth_failure"): 1000.0, ("plc-01", "cmd_inject"): 1045.0}
        self._last_forwarded: dict[tuple[str, str], float] = {}

    def process(self, alert: dict[str, Any]) -> bool:
        """Return True (forward) or False (suppress) for this alert.

        Decision rule: forward if no prior alert for this key, OR if more than
        cooldown_seconds have passed since the last forwarded alert.
        Uses strict > so an alert at exactly the cooldown boundary is still suppressed.
        """
        key     = (alert["device_id"], alert["alert_type"])
        ts      = alert["ts"]
        last_ts = self._last_forwarded.get(key)

        if last_ts is None or (ts - last_ts) > self.cooldown_seconds:
            self._last_forwarded[key] = ts   # anchor new cooldown window
            return True    # forward

        return False   # still within cooldown — suppress

    def reset(self, device_id: str | None = None, alert_type: str | None = None) -> None:
        """Clear cooldown state, optionally scoped to a device or alert_type.

        Call with no arguments to clear all state (e.g. after a maintenance window).
        Call with device_id to clear all cooldowns for that device.
        Call with both to clear a specific (device, type) pair.
        """
        if device_id is None and alert_type is None:
            # Full reset — useful when returning from maintenance
            self._last_forwarded.clear()
        else:
            # Selective reset — filter by whichever fields were specified
            keys_to_remove = [
                k for k in self._last_forwarded
                if (device_id is None   or k[0] == device_id) and
                   (alert_type is None  or k[1] == alert_type)
            ]
            for k in keys_to_remove:
                del self._last_forwarded[k]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_first_alert_forwarded():
    limiter = AlertRateLimiter(cooldown_seconds=60)
    assert limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000}) is True


def test_duplicate_within_cooldown_suppressed():
    limiter = AlertRateLimiter(cooldown_seconds=60)
    limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000})
    assert limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1045}) is False


def test_alert_after_cooldown_forwarded():
    limiter = AlertRateLimiter(cooldown_seconds=60)
    limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000})
    assert limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1061}) is True


def test_different_device_not_suppressed():
    # Each device has its own independent cooldown state
    limiter = AlertRateLimiter(cooldown_seconds=60)
    limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000})
    assert limiter.process({"device_id": "rtu-05", "alert_type": "auth_failure", "ts": 1000}) is True


def test_different_alert_type_not_suppressed():
    # Each alert_type has its own cooldown even on the same device
    limiter = AlertRateLimiter(cooldown_seconds=60)
    limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000})
    assert limiter.process({"device_id": "plc-01", "alert_type": "cmd_inject", "ts": 1000}) is True


def test_reset_clears_state():
    limiter = AlertRateLimiter(cooldown_seconds=60)
    limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000})
    limiter.reset()   # clear all cooldowns
    # After reset, the same alert is treated as new
    assert limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1010}) is True


def test_exact_boundary_still_suppressed():
    limiter = AlertRateLimiter(cooldown_seconds=60)
    limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1000})
    # Gap = exactly 60s — NOT strictly greater than cooldown → suppressed
    assert limiter.process({"device_id": "plc-01", "alert_type": "auth_failure", "ts": 1060}) is False


def test_full_sequence_1000_1045_1060_1061_1090():
    # Mirrors the diagram: FWD, SUPP(45s), SUPP(60s), FWD(61s→reset), SUPP(29s)
    limiter = AlertRateLimiter(cooldown_seconds=60)
    alert = lambda ts: {"device_id": "plc-01", "alert_type": "auth_failure", "ts": ts}
    assert limiter.process(alert(1000)) is True   # first → forward, record 1000
    assert limiter.process(alert(1045)) is False  # 45s gap → suppress
    assert limiter.process(alert(1060)) is False  # 60s gap, not > 60 → suppress
    assert limiter.process(alert(1061)) is True   # 61s gap → forward, reset to 1061
    assert limiter.process(alert(1090)) is False  # 29s from 1061 → suppress


if __name__ == "__main__":
    test_first_alert_forwarded()
    test_duplicate_within_cooldown_suppressed()
    test_alert_after_cooldown_forwarded()
    test_different_device_not_suppressed()
    test_different_alert_type_not_suppressed()
    test_reset_clears_state()
    test_exact_boundary_still_suppressed()
    test_full_sequence_1000_1045_1060_1061_1090()
    print("All tests passed.")
