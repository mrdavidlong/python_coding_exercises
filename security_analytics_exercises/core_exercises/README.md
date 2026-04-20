# Security Analytics Exercises

This repository collects Python exercises around security analytics and event processing.
The focus here is on **practical data manipulation and business logic** - not algorithms.

All questions mirror real engineering work on a security event pipeline: parsing logs, aggregating metrics, applying business rules, and managing alert state.

Each file contains:
- A problem statement docstring with example input/output
- A solution with inline comments
- Runnable tests at the bottom (`python <filename>.py`)

---

## Tier 1 (Top 10)

Core Python data manipulation patterns that any XDR engineer writes constantly.

| # | File | Topic | Key Concepts |
|---|------|--------|--------------|
| 1 | [parse_security_events.py](parse_security_events.py) | Filter event dicts by severity, extract fields | dict access, list comprehension, severity ranking |
| 2 | [aggregate_device_metrics.py](aggregate_device_metrics.py) | Group readings by device, compute min/max/avg | `defaultdict`, `statistics.mean` |
| 3 | [top_n_noisy_devices.py](top_n_noisy_devices.py) | Top N devices by alert count in a time window | `Counter`, `sorted`, tie-breaking |
| 4 | [deduplicate_alerts.py](deduplicate_alerts.py) | Suppress duplicate (device, type) alerts within a window | time-based dedup, sorted scan |
| 5 | [flatten_nested_telemetry.py](flatten_nested_telemetry.py) | Flatten nested JSON telemetry to dot-separated keys | recursive dict walking |
| 6 | [normalize_timestamps.py](normalize_timestamps.py) | Unify epoch/ISO 8601/date-only to UTC datetime | `datetime`, `strptime`, timezone handling |
| 7 | [classify_alert_severity.py](classify_alert_severity.py) | Rule-based classifier: event fields → LOW/MEDIUM/HIGH/CRITICAL | ordered if/elif business rules |
| 8 | [merge_asset_inventory.py](merge_asset_inventory.py) | Merge two asset lists, prefer newest record on conflict | dict merge, conflict resolution |
| 9 | [detect_missing_heartbeats.py](detect_missing_heartbeats.py) | Find devices that missed expected check-ins | set difference, time window |
| 10 | [enrich_events_with_context.py](enrich_events_with_context.py) | Join event stream with device metadata | in-memory dict join, field precedence |

---

## Tier 2 (Next 10)

Domain-specific patterns testing business logic and stateful processing.

| # | File | Topic | Key Concepts |
|---|------|--------|--------------|
| 11 | [threshold_alerting.py](threshold_alerting.py) | Alert when readings exceed threshold N consecutive times | run-length detection, edge cases |
| 12 | [rate_limit_alerts.py](rate_limit_alerts.py) | Suppress duplicate alerts per device within a cooldown | stateful class, per-key timestamps |
| 13 | [track_device_state_machine.py](track_device_state_machine.py) | Track ONLINE→DEGRADED→OFFLINE transitions | state machine dict, invalid transition handling |
| 14 | [compute_uptime_percentage.py](compute_uptime_percentage.py) | Compute per-device uptime % from event log | time delta math, gap detection |
| 15 | [validate_config_schema.py](validate_config_schema.py) | Validate sensor config: required fields, types, value ranges | `isinstance`, schema-driven validation |
| 16 | [parse_csv_report.py](parse_csv_report.py) | Parse incident CSV, compute stats, detect outliers | `csv.DictReader`, `statistics.stdev` |
| 17 | [batch_process_events.py](batch_process_events.py) | Process large event lists in configurable batches | generator, chunking, callable pattern |
| 18 | [group_alerts_by_kill_chain.py](group_alerts_by_kill_chain.py) | Group alerts by cyber kill chain phase | taxonomy mapping, `defaultdict` |
| 19 | [transform_protocol_messages.py](transform_protocol_messages.py) | Normalize Modbus/OPC-UA messages to common schema | field remapping, register maps, datetime parsing |
| 20 | [detect_consecutive_anomalies.py](detect_consecutive_anomalies.py) | Find devices in a sustained anomaly run | reverse scan for trailing run, `defaultdict` |

---

## Tier 3 (Last 10)

More architectural patterns; less likely but good to have ready.

| # | File | Topic | Key Concepts |
|---|------|--------|--------------|
| 21 | [prioritize_alert_queue.py](prioritize_alert_queue.py) | Priority queue: pop by severity then timestamp | `heapq`, tuple comparison, counter tie-break |
| 22 | [rolling_average_metrics.py](rolling_average_metrics.py) | Rolling N-point average for sensor readings | `deque(maxlen=N)`, running sum |
| 23 | [correlate_event_streams.py](correlate_event_streams.py) | Link events from two streams within T seconds | binary search (`bisect`), greedy matching |
| 24 | [build_rule_engine.py](build_rule_engine.py) | Evaluate alert rules from a config list against events | operator dispatch, priority sorting |
| 25 | [data_quality_checks.py](data_quality_checks.py) | Validate event batch: missing fields, nulls, out-of-range | multi-check validation report, `Counter` |
| 26 | [lru_cache_seen_events.py](lru_cache_seen_events.py) | Track recent event fingerprints, evict LRU | `OrderedDict`, LRU eviction pattern |
| 27 | [generate_summary_report.py](generate_summary_report.py) | Aggregate events into an incident summary report | `Counter.most_common`, timeline building |
| 28 | [cross_reference_allowlist.py](cross_reference_allowlist.py) | Flag events from devices not in the approved allowlist | set membership, partition pattern |
| 29 | [time_bucket_analysis.py](time_bucket_analysis.py) | Bucket events into hourly/daily slots | datetime truncation, `defaultdict` |
| 30 | [parse_alert_suppression_rules.py](parse_alert_suppression_rules.py) | Suppress alerts that fall within maintenance windows | interval overlap, wildcard device matching |

---

## Running All Tests

```bash
# Run all 30 files
for f in *.py; do python "$f" && echo "✓ $f"; done
```

Or individually:
```bash
python parse_security_events.py
python aggregate_device_metrics.py
# ... etc
```

## Key Libraries Used

| Library | Used In |
|---------|---------|
| `collections.defaultdict` | aggregation, grouping |
| `collections.Counter` | counting, top-N |
| `collections.deque` | rolling window, LRU |
| `collections.OrderedDict` | LRU cache |
| `datetime` / `timezone` | timestamp normalization |
| `statistics` | mean, stdev |
| `heapq` | priority queue |
| `bisect` | binary search in sorted list |
| `csv` / `io.StringIO` | CSV parsing without file I/O |
| `itertools` | (available for groupby if needed) |
