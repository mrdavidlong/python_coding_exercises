"""
Problem: OT devices send nested JSON telemetry. Flatten it into a single-level
dict with dot-separated keys so it can be indexed or stored in a flat table.

Example input:
    {
        "device_id": "plc-01",
        "readings": {
            "cpu": {"pct": 45.2, "temp_c": 72},
            "mem": {"used_mb": 512}
        },
        "status": "ONLINE"
    }

Expected output:
    {
        "device_id": "plc-01",
        "readings.cpu.pct": 45.2,
        "readings.cpu.temp_c": 72,
        "readings.mem.used_mb": 512,
        "status": "ONLINE"
    }
"""

from typing import Any


def flatten_telemetry(
    data: dict[str, Any],
    prefix: str = "",
    separator: str = ".",
) -> dict[str, Any]:
    """Recursively flatten a nested dict into dot-separated keys.

    Recursion trace for {"readings": {"cpu": {"pct": 45.2}}}:
      call 1: prefix=""        key="readings"  value={"cpu":...}  → recurse
      call 2: prefix="readings" key="cpu"      value={"pct":...}  → recurse
      call 3: prefix="readings.cpu" key="pct"  value=45.2         → emit "readings.cpu.pct"

    Non-dict values (int, float, str, list, None) are treated as leaves and emitted
    directly. Lists are NOT recursed into — ["ot", "plc"] stays as a list value.

    Args:
        data:      Nested dict to flatten.
                   e.g. {"device":"plc-01","readings":{"cpu":{"pct":45.2},"mem_mb":512}}
        prefix:    Key prefix accumulated during recursion. Callers leave this as "".
        separator: Character between key segments.  e.g. "."  or  "/"

    Returns:
        Flat dict with fully-qualified dot-path keys.
        e.g. {"device":"plc-01","readings.cpu.pct":45.2,"readings.mem_mb":512}
    """
    result: dict[str, Any] = {}
    for key, value in data.items(): #remember to do data.items(), not just
        # Build the fully qualified key: prefix + separator + key, or just key at root
        full_key = f"{prefix}{separator}{key}" if prefix else key

        if isinstance(value, dict):
            # Nested dict → recurse, passing the current full_key as the new prefix
            result.update(flatten_telemetry(value, prefix=full_key, separator=separator)) #remember result.update, not result.append, since result is a dict
        else:
            # Leaf value (int, float, str, list, bool, None) → store directly
            result[full_key] = value
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SAMPLE_TELEMETRY = {
    "device_id": "plc-01",
    "readings": {
        "cpu": {"pct": 45.2, "temp_c": 72},
        "mem": {"used_mb": 512},
    },
    "status": "ONLINE",
}


def test_basic_flatten():
    result = flatten_telemetry(SAMPLE_TELEMETRY)
    assert result["device_id"] == "plc-01"
    assert result["readings.cpu.pct"] == 45.2
    assert result["readings.cpu.temp_c"] == 72
    assert result["readings.mem.used_mb"] == 512
    assert result["status"] == "ONLINE"
    # No nested dicts remain
    assert not any(isinstance(v, dict) for v in result.values())


def test_flat_input_unchanged():
    data = {"a": 1, "b": 2}
    assert flatten_telemetry(data) == {"a": 1, "b": 2}


def test_empty_input():
    assert flatten_telemetry({}) == {}


def test_deep_nesting():
    data = {"a": {"b": {"c": {"d": 42}}}}
    result = flatten_telemetry(data)
    assert result == {"a.b.c.d": 42}


def test_custom_separator():
    data = {"a": {"b": 1}}
    result = flatten_telemetry(data, separator="/")
    assert "a/b" in result


def test_list_values_preserved():
    # Lists are treated as leaf values (not recursed into)
    data = {"tags": ["ot", "plc"], "level": 1}
    result = flatten_telemetry(data)
    assert result["tags"] == ["ot", "plc"]


if __name__ == "__main__":
    test_basic_flatten()
    test_flat_input_unchanged()
    test_empty_input()
    test_deep_nesting()
    test_custom_separator()
    test_list_values_preserved()
    print("All tests passed.")
