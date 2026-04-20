"""

Problem
You are given a list of security findings. Each finding has:

asset_id
severity in ["low", "medium", "high", "critical"]
status in ["open", "resolved"]
timestamp
source

Return a summary per asset_id with:

number of open findings
highest open severity
latest finding timestamp
sources that reported open findings
output sorted by highest severity first, then open count descending, then latest timestamp

"""
from collections import defaultdict
from datetime import datetime
from typing import Any

SEVERITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

def summarize_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Summarize open findings per asset.

    Args:
        findings: list[dict]
            Each finding should include:
            - asset_id
            - severity: low, medium, high, or critical
            - status: open or resolved
            - timestamp: ISO-8601 timestamp string
            - source: scanner or source name

    Returns:
        list[dict]:
            One summary per asset with:
            - asset_id
            - open_count
            - highest_open_severity
            - latest_timestamp
            - open_sources

    Example:
        summarize_findings([
            {
                "asset_id": "asset1",
                "severity": "high",
                "status": "open",
                "timestamp": "2025-02-01T10:00:00",
                "source": "scanner1",
            }
        ])
        # [{"asset_id": "asset1", "open_count": 1, ...}]
    """
    # Example key/value:
    # "asset1" -> [{"asset_id": "asset1", "severity": "high", ...}, {...}]
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    # Group rows by asset so each asset can be summarized independently.
    for finding in findings:
        grouped[finding["asset_id"]].append(finding)

    # Example summary row:
    # {"asset_id": "asset1", "open_count": 2, "highest_open_severity": "high", ...}
    summaries: list[dict[str, Any]] = []

    for asset_id, rows in grouped.items():
        # Example open row: {"asset_id": "asset1", "status": "open", "source": "scanner1", ...}
        open_rows: list[dict[str, Any]] = [r for r in rows if r["status"] == "open"]

        if open_rows:
            # Highest severity among open rows becomes the asset severity.
            highest_open_severity: str | None = max(open_rows, key=lambda r: SEVERITY_RANK[r["severity"]])["severity"]
            open_count: int = len(open_rows)
            open_sources: list[str] = sorted({r["source"] for r in open_rows})
        else:
            highest_open_severity = None
            open_count = 0
            open_sources = []

        latest_ts: str = max(r["timestamp"] for r in rows)

        summaries.append({
            "asset_id": asset_id,
            "open_count": open_count,
            "highest_open_severity": highest_open_severity,
            "latest_timestamp": latest_ts,
            "open_sources": open_sources,
        })

    def sort_key(item: dict[str, Any]) -> tuple[int, int, int]:
        # Sort by severity first, then open count, then recency.
        severity_score = SEVERITY_RANK[item["highest_open_severity"]] if item["highest_open_severity"] else 0
        return (-severity_score, -item["open_count"], -to_epoch(item["latest_timestamp"]))

    return sorted(summaries, key=sort_key)

def to_epoch(ts: str) -> int:
    return int(datetime.fromisoformat(ts).timestamp())

def test_empty_findings() -> None:
    result = summarize_findings([])
    # Empty input should produce no summary rows.
    assert result == []


def test_single_asset_single_open_finding() -> None:
    findings = [{
        "asset_id": "asset1",
        "severity": "high",
        "status": "open",
        "timestamp": "2025-02-01T10:00:00",
        "source": "scanner1",
    }]
    result = summarize_findings(findings)
    # One open finding becomes one summary row with matching metadata.
    assert len(result) == 1
    assert result[0]["asset_id"] == "asset1"
    assert result[0]["open_count"] == 1
    assert result[0]["highest_open_severity"] == "high"
    assert result[0]["open_sources"] == ["scanner1"]


def test_multiple_assets_sorted_by_severity() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "low",
            "status": "open",
            "timestamp": "2025-02-01T10:00:00",
            "source": "scanner1",
        },
        {
            "asset_id": "asset2",
            "severity": "critical",
            "status": "open",
            "timestamp": "2025-02-01T10:00:00",
            "source": "scanner1",
        },
    ]
    result = summarize_findings(findings)
    # Critical severity should rank ahead of low severity.
    assert result[0]["asset_id"] == "asset2"
    assert result[0]["highest_open_severity"] == "critical"


def test_resolved_findings_excluded() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "critical",
            "status": "resolved",
            "timestamp": "2025-02-01T10:00:00",
            "source": "scanner1",
        },
        {
            "asset_id": "asset1",
            "severity": "low",
            "status": "open",
            "timestamp": "2025-02-01T11:00:00",
            "source": "scanner2",
        },
    ]
    result = summarize_findings(findings)
    # Resolved findings do not count toward open_count or open_sources.
    assert result[0]["open_count"] == 1
    assert result[0]["highest_open_severity"] == "low"
    assert result[0]["open_sources"] == ["scanner2"]


def test_multiple_open_findings_same_asset() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "high",
            "status": "open",
            "timestamp": "2025-02-01T10:00:00",
            "source": "scanner1",
        },
        {
            "asset_id": "asset1",
            "severity": "medium",
            "status": "open",
            "timestamp": "2025-02-01T11:00:00",
            "source": "scanner2",
        },
    ]
    result = summarize_findings(findings)
    # Both open rows count, and the highest severity remains high.
    assert result[0]["open_count"] == 2
    assert result[0]["highest_open_severity"] == "high"
    assert sorted(result[0]["open_sources"]) == ["scanner1", "scanner2"]


def test_sorted_by_open_count_then_timestamp() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "high",
            "status": "open",
            "timestamp": "2025-02-01T10:00:00",
            "source": "scanner1",
        },
        {
            "asset_id": "asset1",
            "severity": "high",
            "status": "open",
            "timestamp": "2025-02-01T11:00:00",
            "source": "scanner2",
        },
        {
            "asset_id": "asset2",
            "severity": "high",
            "status": "open",
            "timestamp": "2025-02-01T12:00:00",
            "source": "scanner1",
        },
    ]
    result = summarize_findings(findings)
    # Ties on severity break by open count, then by latest timestamp.
    assert result[0]["asset_id"] == "asset1"
    assert result[0]["open_count"] == 2


if __name__ == "__main__":
    test_empty_findings()
    test_single_asset_single_open_finding()
    test_multiple_assets_sorted_by_severity()
    test_resolved_findings_excluded()
    test_multiple_open_findings_same_asset()
    test_sorted_by_open_count_then_timestamp()
    print("All tests passed.")
