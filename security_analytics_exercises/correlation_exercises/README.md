# Security Analytics Exercises - Correlation Exercises

This folder contains a smaller set of security-correlation exercises that focus on finding relationships across event streams and security findings.

## Included Exercises

- `correlate_events_into_findings.py`
- `dedupe_alerts_from_multiple_tools.py`
- `detect_repeated_failed_logins.py`
- `find_device_open_status_logs.py`
- `prioritize_assets_by_risk_score.py`
- `reconstruct_latest_state_from_change_history.py`

## Running

Each file can be run directly:

```bash
python correlation_exercises/correlate_events_into_findings.py
python correlation_exercises/prioritize_assets_by_risk_score.py
```

The root `pytest.ini` also includes this folder, so `pytest` from the project root will discover these files as well.
