# Security Analytics Exercises

This project is a collection of Python exercises centered on security analytics, alert processing, and event correlation.

## Layout

- `core_exercises/` contains the larger set of standalone exercises and supporting mocks
- `correlation_exercises/` contains a smaller set of focused security correlation exercises

## Running Tests

From the project root:

```bash
pytest
```

The root `pytest.ini` keeps test discovery pointed at `core_exercises` and `correlation_exercises`, so you do not need to move it.

You can also run any exercise directly:

```bash
python core_exercises/rolling_average_metrics.py
python correlation_exercises/correlate_events_into_findings.py
```

## Notes

- Each exercise file includes its own inline tests.
- The examples are intentionally small and practical, matching the kind of logic used in security telemetry pipelines.
