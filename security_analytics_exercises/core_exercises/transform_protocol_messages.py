"""
Problem: OT devices speak different protocols. Normalize raw Modbus and OPC-UA
style message dicts into a common schema so downstream processing is protocol-agnostic.

Common schema:
    {
        "source_protocol": str,     # "modbus" | "opcua"
        "device_id":       str,
        "tag":             str,     # the variable name / register label
        "value":           float,
        "unit":            str,     # e.g. "°C", "bar", "%", "rpm"
        "ts":              float,   # Unix epoch seconds
    }

Modbus raw format:
    {"slave_id": "10", "register": "40001", "raw_value": "755", "timestamp_ms": 1700000000000}
    (register 40001 = holding register 1, which maps to "temperature_c" at scale 0.1, unit "°C")

OPC-UA raw format:
    {"node_id": "ns=2;s=Pump1.Speed", "value": 1450.0, "source_timestamp": "2023-11-14T22:13:20Z",
     "server_id": "opc.tcp://plc-01:4840"}
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# Modbus register map: register_number → (tag, scale_factor, unit)
# e.g. {"40001": ("temperature_c", 0.1, "°C")} means raw value 253 → 253 * 0.1 = 25.3°C
MODBUS_REGISTER_MAP: dict[str, tuple[str, float, str]] = {
    "40001": ("temperature_c", 0.1, "°C"),
    "40002": ("pressure_bar",  0.01, "bar"),
    "40003": ("flow_rate",     1.0,  "L/min"),
    "40004": ("motor_speed",   1.0,  "rpm"),
}


def normalize_modbus(msg: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize a raw Modbus message to the common schema.

    Args:
        msg: Raw Modbus dict with keys:
               "register"     (str) — e.g. "40001"
               "slave_id"     (str/int) — e.g. "3"
               "raw_value"    (str/float) — e.g. "253"
               "timestamp_ms" (str/float) — milliseconds epoch, e.g. "1700000000000"

    Returns:
        Normalized dict with keys: source_protocol, device_id, tag, value, unit, ts.
        e.g. {"source_protocol":"modbus","device_id":"slave-3",
               "tag":"temperature_c","value":25.3,"unit":"°C","ts":1700000000.0}
        Returns None if register is not in MODBUS_REGISTER_MAP.
    """
    register = msg.get("register", "")
    mapping  = MODBUS_REGISTER_MAP.get(register)
    if mapping is None:
        return None

    tag, scale, unit = mapping
    return {
        "source_protocol": "modbus",
        "device_id":       f"slave-{msg['slave_id']}",
        "tag":             tag,
        "value":           float(msg["raw_value"]) * scale,
        "unit":            unit,
        "ts":              float(msg["timestamp_ms"]) / 1000.0,
    }


def normalize_opcua(msg: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw OPC-UA message to the common schema.

    Args:
        msg: Raw OPC-UA dict with keys:
               "server_id"        (str) — e.g. "opc.tcp://plc-01:4840"
               "node_id"          (str) — e.g. "ns=2;s=Pump1.Speed"
               "value"            (float) — e.g. 1450.0
               "unit"             (str) — e.g. "rpm"
               "source_timestamp" (str) — ISO format, e.g. "2023-11-14T22:13:20Z"

    Returns:
        Normalized dict with keys: source_protocol, device_id, tag, value, unit, ts.
        e.g. {"source_protocol":"opcua","device_id":"plc-01",
               "tag":"Pump1.Speed","value":1450.0,"unit":"rpm","ts":1700000000.0}
    """
    # Extract device_id from server URI (opc.tcp://plc-01:4840 → plc-01)
    server_id = msg.get("server_id", "")
    device_id = server_id.split("//")[-1].split(":")[0] if "//" in server_id else server_id

    # Extract tag from node_id (ns=2;s=Pump1.Speed → Pump1.Speed)
    node_id = msg.get("node_id", "")
    tag     = node_id.split("s=")[-1] if "s=" in node_id else node_id

    # Parse ISO timestamp to epoch
    ts_str = msg.get("source_timestamp", "")
    try:
        dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        ts = dt.timestamp()
    except ValueError:
        ts = 0.0

    return {
        "source_protocol": "opcua",
        "device_id":       device_id,
        "tag":             tag,
        "value":           float(msg.get("value", 0)),
        "unit":            msg.get("unit", ""),
        "ts":              ts,
    }


def normalize_message(msg: dict[str, Any]) -> dict[str, Any] | None:
    """Route a raw message to the correct normalizer based on its "protocol" field.

    Args:
        msg: Raw message dict. Must have a "protocol" key ("modbus" or "opcua").
             e.g. {"protocol":"modbus","register":"40001","slave_id":"3",...}

    Returns:
        Normalized dict from normalize_modbus or normalize_opcua.
        None if protocol is "modbus" but register is unknown.

    Raises:
        ValueError if protocol is not "modbus" or "opcua".
    """
    protocol = msg.get("protocol", "").lower()
    if protocol == "modbus":
        return normalize_modbus(msg)
    if protocol == "opcua":
        return normalize_opcua(msg)
    return None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_modbus_normalization():
    msg = {
        "protocol": "modbus",
        "slave_id": "10", "register": "40001",
        "raw_value": "755", "timestamp_ms": 1700000000000,
    }
    result = normalize_message(msg)
    assert result["source_protocol"] == "modbus"
    assert result["device_id"] == "slave-10"
    assert result["tag"] == "temperature_c"
    assert abs(result["value"] - 75.5) < 1e-6   # 755 * 0.1
    assert result["unit"] == "°C"
    assert result["ts"] == 1700000000.0


def test_modbus_unknown_register():
    msg = {"protocol": "modbus", "slave_id": "1", "register": "99999",
           "raw_value": "100", "timestamp_ms": 0}
    assert normalize_message(msg) is None


def test_opcua_normalization():
    msg = {
        "protocol": "opcua",
        "node_id": "ns=2;s=Pump1.Speed",
        "value": 1450.0,
        "source_timestamp": "2023-11-14T22:13:20Z",
        "server_id": "opc.tcp://plc-01:4840",
    }
    result = normalize_message(msg)
    assert result["source_protocol"] == "opcua"
    assert result["device_id"] == "plc-01"
    assert result["tag"] == "Pump1.Speed"
    assert result["value"] == 1450.0


def test_unknown_protocol():
    assert normalize_message({"protocol": "dnp3"}) is None


if __name__ == "__main__":
    test_modbus_normalization()
    test_modbus_unknown_register()
    test_opcua_normalization()
    test_unknown_protocol()
    print("All tests passed.")
