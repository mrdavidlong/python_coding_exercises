"""
Problem: Before deploying a sensor config, validate it against a schema that
specifies required fields, their expected types, and optional value constraints.

Schema format:
    {
        "field_name": {
            "type": int | float | str | bool | list,
            "required": True/False,
            "min": <optional numeric lower bound>,
            "max": <optional numeric upper bound>,
            "allowed": <optional list of allowed values>,
        }
    }

Return a list of human-readable validation error strings (empty = valid config).

Example input:
    schema = {
        "device_id":      {"type": str,  "required": True},
        "poll_interval_s":{"type": int,  "required": True, "min": 1, "max": 3600},
        "protocol":       {"type": str,  "required": True, "allowed": ["modbus", "opcua", "dnp3"]},
        "enabled":        {"type": bool, "required": False},
    }
    config = {"device_id": "plc-01", "poll_interval_s": 0, "protocol": "http"}

Expected errors:
    ["poll_interval_s: value 0 is below minimum 1",
     "protocol: value 'http' not in allowed values ['dnp3', 'modbus', 'opcua']"]
"""

from typing import Any


def validate_config(
    config: dict[str, Any],
    schema: dict[str, dict[str, Any]],
) -> list[str]:
    """Validate a config dict against a schema. Returns all errors in one pass.

    Validation is non-short-circuiting: ALL fields are checked so the caller
    gets a complete list of errors in one call rather than fixing one at a time.

    Check order per field:
      1. Presence  — skip optional absent fields; error on missing required ones.
      2. Type      — stop further checks for this field if type is wrong
                     (range/allowlist checks would be meaningless on the wrong type).
      3. Range     — min/max bounds (numeric fields only).
      4. Allowlist — value must be in the declared set of legal values.

    Args:
        config: The config dict to validate.
                e.g. {"sample_rate": 150, "protocol": "modbus", "enabled": True}
        schema: Field name → rules dict. Supported rule keys:
                  "required"  (bool)  — error if field absent
                  "type"      (type)  — e.g. int, float, str
                  "min"       (num)   — inclusive lower bound
                  "max"       (num)   — inclusive upper bound
                  "allowed"   (set)   — value must be in this set
                e.g. {"sample_rate": {"required": True, "type": int, "min": 1, "max": 3600},
                       "protocol":   {"required": True, "type": str,
                                      "allowed": {"modbus","opcua","dnp3"}}}

    Returns:
        List of human-readable error strings. Empty list means the config is valid.
        e.g. ["sample_rate: value 150 exceeds max 100",
               "protocol: value 'zigbee' not in allowed set"]
    """
    errors: list[str] = []

    for field, rules in schema.items():
        value    = config.get(field)   # None if absent
        required = rules.get("required", False)

        # Step 1: check presence
        if value is None:
            if required:
                errors.append(f"{field}: required field is missing")
            continue  # absent optional field — nothing more to check

        # Step 2: check type — early continue prevents nonsensical range checks
        # (e.g., comparing a string to a numeric min would raise TypeError)
        expected_type = rules.get("type")
        if expected_type and not isinstance(value, expected_type):
            errors.append(
                f"{field}: expected type {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
            continue  # type mismatch — remaining checks don't apply

        if "min" in rules and value < rules["min"]:
            errors.append(f"{field}: value {value} is below minimum {rules['min']}")

        if "max" in rules and value > rules["max"]:
            errors.append(f"{field}: value {value} exceeds maximum {rules['max']}")

        if "allowed" in rules and value not in rules["allowed"]:
            allowed_sorted = sorted(str(v) for v in rules["allowed"])
            errors.append(
                f"{field}: value {value!r} not in allowed values {allowed_sorted}"
            )

    return errors


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SCHEMA = {
    "device_id":       {"type": str,  "required": True},
    "poll_interval_s": {"type": int,  "required": True, "min": 1, "max": 3600},
    "protocol":        {"type": str,  "required": True, "allowed": ["modbus", "opcua", "dnp3"]},
    "enabled":         {"type": bool, "required": False},
}


def test_valid_config():
    config = {"device_id": "plc-01", "poll_interval_s": 30, "protocol": "modbus", "enabled": True}
    assert validate_config(config, SCHEMA) == []


def test_missing_required_field():
    config = {"poll_interval_s": 30, "protocol": "modbus"}
    errors = validate_config(config, SCHEMA)
    assert any("device_id" in e and "missing" in e for e in errors)


def test_value_below_min():
    config = {"device_id": "plc-01", "poll_interval_s": 0, "protocol": "modbus"}
    errors = validate_config(config, SCHEMA)
    assert any("poll_interval_s" in e and "below minimum" in e for e in errors)


def test_value_above_max():
    config = {"device_id": "plc-01", "poll_interval_s": 9999, "protocol": "modbus"}
    errors = validate_config(config, SCHEMA)
    assert any("poll_interval_s" in e and "exceeds maximum" in e for e in errors)


def test_invalid_allowed_value():
    config = {"device_id": "plc-01", "poll_interval_s": 30, "protocol": "http"}
    errors = validate_config(config, SCHEMA)
    assert any("protocol" in e and "allowed" in e for e in errors)


def test_wrong_type():
    config = {"device_id": "plc-01", "poll_interval_s": "thirty", "protocol": "modbus"}
    errors = validate_config(config, SCHEMA)
    assert any("poll_interval_s" in e and "expected type" in e for e in errors)


def test_optional_field_absent_is_ok():
    config = {"device_id": "plc-01", "poll_interval_s": 60, "protocol": "opcua"}
    # 'enabled' is optional — missing it should not raise an error
    errors = validate_config(config, SCHEMA)
    assert not any("enabled" in e for e in errors)


def test_multiple_errors_returned():
    config = {"poll_interval_s": 0, "protocol": "http"}  # missing device_id, bad interval, bad protocol
    errors = validate_config(config, SCHEMA)
    assert len(errors) >= 3


if __name__ == "__main__":
    test_valid_config()
    test_missing_required_field()
    test_value_below_min()
    test_value_above_max()
    test_invalid_allowed_value()
    test_wrong_type()
    test_optional_field_absent_is_ok()
    test_multiple_errors_returned()
    print("All tests passed.")
