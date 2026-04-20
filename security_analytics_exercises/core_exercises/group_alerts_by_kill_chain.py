"""
Problem: Group security alerts by their cyber kill chain phase so an analyst
can see which phases are active during an incident.

Kill chain phases (Lockheed Martin model):
    1. Reconnaissance
    2. Weaponization
    3. Delivery
    4. Exploitation
    5. Installation
    6. Command & Control (C2)
    7. Actions on Objectives

Each alert has an alert_type. Map alert types to phases using a taxonomy dict,
then group alerts by phase. Unknown types go to an "Unclassified" bucket.

Example input:
    alerts = [
        {"id": "a1", "alert_type": "port_scan"},
        {"id": "a2", "alert_type": "phishing_email"},
        {"id": "a3", "alert_type": "c2_beacon"},
        {"id": "a4", "alert_type": "unknown_type"},
    ]

Expected output:
    {
        "Reconnaissance": [{"id": "a1", ...}],
        "Delivery":       [{"id": "a2", ...}],
        "C2":             [{"id": "a3", ...}],
        "Unclassified":   [{"id": "a4", ...}],
    }
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

# Taxonomy: alert_type → kill chain phase
ALERT_TYPE_TO_PHASE: dict[str, str] = {
    # Reconnaissance
    "port_scan":        "Reconnaissance",
    "host_enumeration": "Reconnaissance",
    "vuln_scan":        "Reconnaissance",
    # Delivery
    "phishing_email":   "Delivery",
    "usb_insertion":    "Delivery",
    "malicious_file":   "Delivery",
    # Exploitation
    "exploit_attempt":  "Exploitation",
    "cmd_inject":       "Exploitation",
    "buffer_overflow":  "Exploitation",
    # Installation
    "malware_install":  "Installation",
    "firmware_tamper":  "Installation",
    "persistence_set":  "Installation",
    # C2
    "c2_beacon":        "C2",
    "dns_tunnel":       "C2",
    "reverse_shell":    "C2",
    # Actions on Objectives
    "data_exfil":       "Actions on Objectives",
    "safety_override":  "Actions on Objectives",
    "plc_cmd_write":    "Actions on Objectives",
}


def group_by_kill_chain(
    alerts: list[dict[str, Any]],
    taxonomy: dict[str, str] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Group alerts by cyber kill chain phase using an alert_type → phase mapping.

    Args:
        alerts:   List of alert dicts, each with an "alert_type" key.
                  e.g. [{"id":"a1","alert_type":"port_scan","device_id":"plc-01"},
                         {"id":"a2","alert_type":"cmd_inject","device_id":"rtu-05"}]
        taxonomy: Optional override for the default ALERT_TYPE_TO_PHASE mapping.
                  e.g. {"port_scan":"Reconnaissance","cmd_inject":"Execution"}
                  Pass None to use the built-in mapping.

    Returns:
        Dict mapping kill chain phase → list of alerts in that phase.
        Unknown alert_types are placed in "Unclassified".
        e.g. {"Reconnaissance":[{"id":"a1",...}], "Execution":[{"id":"a2",...}]}
    """
    mapping = taxonomy if taxonomy is not None else ALERT_TYPE_TO_PHASE
    # e.g. {"Reconnaissance": [{alert1}, {alert2}], "Command & Control": [{alert3}]}
    groups: dict[str, list] = defaultdict(list)

    for alert in alerts:
        phase = mapping.get(alert.get("alert_type", ""), "Unclassified")
        groups[phase].append(alert)

    return dict(groups)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SAMPLE_ALERTS = [
    {"id": "a1", "alert_type": "port_scan"},
    {"id": "a2", "alert_type": "phishing_email"},
    {"id": "a3", "alert_type": "c2_beacon"},
    {"id": "a4", "alert_type": "safety_override"},
    {"id": "a5", "alert_type": "unknown_type"},
    {"id": "a6", "alert_type": "port_scan"},  # second recon alert
]


def test_known_types_grouped_correctly():
    result = group_by_kill_chain(SAMPLE_ALERTS)
    assert len(result["Reconnaissance"]) == 2
    assert len(result["Delivery"]) == 1
    assert len(result["C2"]) == 1
    assert len(result["Actions on Objectives"]) == 1


def test_unknown_type_goes_to_unclassified():
    result = group_by_kill_chain(SAMPLE_ALERTS)
    assert any(a["id"] == "a5" for a in result["Unclassified"])


def test_custom_taxonomy():
    taxonomy = {"heartbeat": "Noise"}
    alerts   = [{"id": "x", "alert_type": "heartbeat"}]
    result   = group_by_kill_chain(alerts, taxonomy=taxonomy)
    assert "Noise" in result


def test_empty_input():
    assert group_by_kill_chain([]) == {}


def test_all_unclassified():
    alerts = [{"id": "x", "alert_type": "made_up_type"}]
    result = group_by_kill_chain(alerts)
    assert list(result.keys()) == ["Unclassified"]


if __name__ == "__main__":
    test_known_types_grouped_correctly()
    test_unknown_type_goes_to_unclassified()
    test_custom_taxonomy()
    test_empty_input()
    test_all_unclassified()
    print("All tests passed.")
