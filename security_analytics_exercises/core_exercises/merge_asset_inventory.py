"""
Problem: Two asset inventory lists need to be merged. Each asset is identified
by device_id. When the same device_id appears in both lists, keep the record
with the later `last_seen` timestamp. New devices from either list are included.

Example input:
    list_a = [
        {"device_id": "plc-01", "ip": "10.0.0.1", "last_seen": 1700000100},
        {"device_id": "rtu-05", "ip": "10.0.0.5", "last_seen": 1700000050},
    ]
    list_b = [
        {"device_id": "plc-01", "ip": "10.0.0.1", "last_seen": 1700000200},  # newer
        {"device_id": "hmi-03", "ip": "10.0.0.3", "last_seen": 1700000150},  # new device
    ]

Expected output (3 devices, plc-01 from list_b):
    [
        {"device_id": "hmi-03", "ip": "10.0.0.3", "last_seen": 1700000150},
        {"device_id": "plc-01", "ip": "10.0.0.1", "last_seen": 1700000200},
        {"device_id": "rtu-05", "ip": "10.0.0.5", "last_seen": 1700000050},
    ]
"""

from typing import Any


def merge_asset_inventory(
    list_a: list[dict[str, Any]],
    list_b: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge two asset inventory lists, keeping the most recently seen record per device.

    On conflict (same device_id in both lists), the record with the later
    last_seen timestamp wins. Classic upsert: insert if absent, update if newer.

    Args:
        list_a: First asset list. Each dict must have "device_id" and "last_seen".
                e.g. [{"device_id":"plc-01","ip":"10.0.0.1","last_seen":1000}]
        list_b: Second asset list, same format.
                e.g. [{"device_id":"plc-01","ip":"10.0.0.2","last_seen":2000},
                       {"device_id":"rtu-05","ip":"10.0.0.5","last_seen":1500}]

    Returns:
        Merged list sorted by device_id. Winner is the record with the larger last_seen.
        e.g. [{"device_id":"plc-01","ip":"10.0.0.2","last_seen":2000},
               {"device_id":"rtu-05","ip":"10.0.0.5","last_seen":1500}]
    """
    # Build a working dict from list_a — O(n) and gives us O(1) lookup by device_id
    # e.g. {"plc-01": {"device_id": "plc-01", "ip": "10.0.0.1", "last_seen": 1000}, ...}
    merged: dict[str, dict[str, Any]] = {a["device_id"]: a for a in list_a}

    for asset in list_b:
        device_id = asset["device_id"]
        existing  = merged.get(device_id) #remember .get(device_id) return None.  merged[device_id] would raise KeyError

        # alternative (better):
        # if existing is None or asset["last_seen"] > existing["last_seen"]:
        #     merged[device_id] = asset
        if existing is None:
            # New device — not in list_a at all; just insert it
            merged[device_id] = asset #remember it's the value device_id not the string "device_id" here
        elif asset["last_seen"] > existing["last_seen"]: #remember, it's asset["seen"], not asset[device_id]["last_seen"] 
            # Same device, but list_b has a more recent record — replace
            merged[device_id] = asset
        # else: list_a's record is newer or equal — keep it, discard list_b entry

    # Sort output for determinism — dict order is insertion order, which is
    # arbitrary when merging two sources
    # alternative
    # result = []
    # for a in merged:
    #   result.append(merged[a])
    # result.sort(key=lambda x: x["device_id"])
    # return result
    return sorted(merged.values(), key=lambda a: a["device_id"])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

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
