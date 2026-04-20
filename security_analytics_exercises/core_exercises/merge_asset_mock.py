from typing import Any

def merge_asset_inventory(
    list_a: list[dict],
    list_b: list[dict]
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {a["device_id"]: a for a in list_a}

    for asset in list_b:
        device_id = asset["device_id"]
        existing = merged.get(device_id)

        if existing is None or asset["last_seen"] > merged[device_id]["last_seen"]:
            merged[device_id] = asset
        # elif asset["last_seen"] > merged[device_id]["last_seen"] :
        #     merged[device_id] = asset

    result = []
    for a in merged:
        result.append(merged[a])
    result.sort(key=lambda x: x["device_id"])
    return result

LIST_A = [
    {"device_id": "plc-01", "ip": "10.0.0.1", "last_seen": 1700000100},
    {"device_id": "rtu-05", "ip": "10.0.0.5", "last_seen": 1700000050},
]
LIST_B = [
    {"device_id": "plc-01", "ip": "10.0.0.1", "last_seen": 1700000200},
    {"device_id": "hmi-03", "ip": "10.0.0.3", "last_seen": 1700000150},
]


def test_newer_record_wins():
    result = merge_asset_inventory(LIST_A, LIST_B)
    plc01 = next(a for a in result if a["device_id"] == "plc-01")
    assert plc01["last_seen"] == 1700000200

def test_new_device_from_b_included():
    result = merge_asset_inventory(LIST_A, LIST_B)
    ids = {a["device_id"] for a in result}
    assert "hmi-03" in ids


def test_device_only_in_a_preserved():
    result = merge_asset_inventory(LIST_A, LIST_B)
    ids = {a["device_id"] for a in result}
    assert "rtu-05" in ids


def test_total_count():
    result = merge_asset_inventory(LIST_A, LIST_B)
    assert len(result) == 3


def test_older_record_in_b_does_not_overwrite():
    a = [{"device_id": "d1", "ip": "1.1.1.1", "last_seen": 1000}]
    b = [{"device_id": "d1", "ip": "2.2.2.2", "last_seen": 500}]  # older
    result = merge_asset_inventory(a, b)
    assert result[0]["ip"] == "1.1.1.1"


def test_empty_lists():
    assert merge_asset_inventory([], []) == []
    assert len(merge_asset_inventory(LIST_A, [])) == 2
    assert len(merge_asset_inventory([], LIST_B)) == 2


if __name__ == "__main__":
    test_newer_record_wins()
    test_new_device_from_b_included()
    test_device_only_in_a_preserved()
    test_total_count()
    test_older_record_in_b_does_not_overwrite()
    test_empty_lists()
    print("All tests passed.")
