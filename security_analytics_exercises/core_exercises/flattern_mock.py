from typing import Any


def flatten_telemetry(
    data: dict[str, Any],
    prefix: str = "",
    separator: str = ".",
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_telemetry(value, prefix=full_key, separator=separator))
        else:
            result[full_key] = value
    return result


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

if __name__ == "__main__":
    test_basic_flatten()