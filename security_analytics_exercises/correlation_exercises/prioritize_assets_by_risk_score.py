"""
Prioritize assets by risk score

Question

Given findings:

asset_id
severity
is_externally_exposed
is_critical_production
status

Compute a risk score per asset:

severity weights: low 1, medium 3, high 6, critical 10
add 5 if externally exposed
add 7 if critical production
only count open findings

Return top 5 risky assets.

What this tests
Dictionary accumulation and business-rule composition.
"""

import heapq
from collections import defaultdict
from typing import Any

SEV_WEIGHT = {
    "low": 1,
    "medium": 3,
    "high": 6,
    "critical": 10,
}


def top_risky_assets(findings: list[dict[str, Any]], top_n: int = 5) -> list[tuple[str, int]]:
    """
    Rank assets by accumulated risk score.

    Args:
        findings: list[dict]
            Each finding should include:
            - asset_id
            - severity
            - status
            - is_externally_exposed
            - is_critical_production
        top_n: int
            Maximum number of ranked assets to return.

    Returns:
        list[tuple[str, int]]:
            Tuples of (asset_id, score), sorted by score desc then asset_id asc.

    Example:
        top_risky_assets([
            {
                "asset_id": "asset1",
                "severity": "critical",
                "status": "open",
                "is_externally_exposed": True,
                "is_critical_production": False,
            }
        ])
        # [("asset1", 15)]
    """
    # Example key/value:
    # "asset1" -> 15, meaning the asset has accumulated 15 risk points.
    scores: defaultdict[str, int] = defaultdict(int)

    for f in findings:
        if f["status"] != "open":
            continue

        # Base score comes from severity, then add business-rule bonuses.
        # Example: a critical open finding starts at 10 points.
        score: int = SEV_WEIGHT[f["severity"]]
        if f.get("is_externally_exposed"):
            score += 5
        if f.get("is_critical_production"):
            score += 7

        scores[f["asset_id"]] += score

    if top_n <= 0:
        return []

    # Ranking choices:
    # 1) heapq.nsmallest(...) or heapq.nlargest(...)
    #    Time: O(A log N), Space: O(N)
    #    A = number of distinct assets after scoring
    #    N = top_n
    # 2) sorted(... )[:top_n]
    #    Time: O(A log A), Space: O(A)
    #
    # We pick the heap-based version because we only need the top N assets
    # and N is small (default 5), so we avoid fully sorting every asset.
    # heapq is always a min-heap, so nsmallest uses the smallest key first.
    # To make higher risk score rank first, we negate the score in the key.
    #
    # We use nsmallest with the key (-score, asset_id):
    # - higher scores become smaller negative numbers
    # - ties still break by asset_id ascending
    # That makes the "best" asset the smallest key.
    ranked: list[tuple[str, int]] = heapq.nsmallest(
        top_n,
        scores.items(),
        key=lambda item: (-item[1], item[0]),
    )

    # Equivalent alternative:
    # ranked = heapq.nlargest(top_n, scores.items(), key=lambda item: (item[1], item[0]))
    # This also has O(A log N) time and O(N) space.
    # We would use the positive score directly, and asset_id still breaks ties.
    #
    # Simpler alternative:
    # ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:top_n]
    # This is easier to read, but it sorts every asset even when we only need a few.

    return ranked


def test_no_findings() -> None:
    result = top_risky_assets([])
    # No open findings means no ranked assets.
    assert result == []


def test_no_open_findings() -> None:
    findings = [{
        "asset_id": "asset1",
        "severity": "critical",
        "status": "resolved",
        "is_externally_exposed": True,
        "is_critical_production": True,
    }]
    result = top_risky_assets(findings)
    # Resolved findings are excluded entirely from scoring.
    assert result == []


def test_single_open_finding() -> None:
    findings = [{
        "asset_id": "asset1",
        "severity": "low",
        "status": "open",
        "is_externally_exposed": False,
        "is_critical_production": False,
    }]
    result = top_risky_assets(findings)
    # A single open low-severity finding scores 1.
    assert result == [("asset1", 1)]


def test_severity_weights() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "low",
            "status": "open",
            "is_externally_exposed": False,
            "is_critical_production": False,
        },
        {
            "asset_id": "asset2",
            "severity": "critical",
            "status": "open",
            "is_externally_exposed": False,
            "is_critical_production": False,
        },
    ]
    result = top_risky_assets(findings)
    # Critical severity should outrank low severity because it has the higher weight.
    assert result[0][0] == "asset2"
    assert result[0][1] == 10


def test_externally_exposed_bonus() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "low",
            "status": "open",
            "is_externally_exposed": True,
            "is_critical_production": False,
        },
    ]
    result = top_risky_assets(findings)
    # External exposure adds 5 to the severity score.
    assert result[0][1] == 6  # 1 + 5


def test_critical_production_bonus() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "low",
            "status": "open",
            "is_externally_exposed": False,
            "is_critical_production": True,
        },
    ]
    result = top_risky_assets(findings)
    # Critical production adds 7 to the severity score.
    assert result[0][1] == 8  # 1 + 7


def test_both_bonuses() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "critical",
            "status": "open",
            "is_externally_exposed": True,
            "is_critical_production": True,
        },
    ]
    result = top_risky_assets(findings)
    # Both bonuses stack on top of the severity weight.
    assert result[0][1] == 22  # 10 + 5 + 7


def test_top_n_limit() -> None:
    findings = [
        {
            "asset_id": f"asset{i}",
            "severity": "critical",
            "status": "open",
            "is_externally_exposed": False,
            "is_critical_production": False,
        }
        for i in range(10)
    ]
    result = top_risky_assets(findings, top_n=5)
    # top_n trims the result list to the requested length.
    assert len(result) == 5


def test_accumulated_score() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "low",
            "status": "open",
            "is_externally_exposed": False,
            "is_critical_production": False,
        },
        {
            "asset_id": "asset1",
            "severity": "medium",
            "status": "open",
            "is_externally_exposed": False,
            "is_critical_production": False,
        },
    ]
    result = top_risky_assets(findings)
    # The two findings for the same asset accumulate into one total score.
    assert result[0][1] == 4  # 1 + 3


def test_tie_breaking_by_asset_id() -> None:
    findings = [
        {
            "asset_id": "asset1",
            "severity": "low",
            "status": "open",
            "is_externally_exposed": False,
            "is_critical_production": False,
        },
        {
            "asset_id": "asset2",
            "severity": "low",
            "status": "open",
            "is_externally_exposed": False,
            "is_critical_production": False,
        },
    ]
    result = top_risky_assets(findings)
    # Equal scores break ties by asset_id ascending.
    assert result[0][0] == "asset1"
    assert result[1][0] == "asset2"


if __name__ == "__main__":
    test_no_findings()
    test_no_open_findings()
    test_single_open_finding()
    test_severity_weights()
    test_externally_exposed_bonus()
    test_critical_production_bonus()
    test_both_bonuses()
    test_top_n_limit()
    test_accumulated_score()
    test_tie_breaking_by_asset_id()
    print("All tests passed.")
