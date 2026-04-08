# app/agents/tools.py
from langchain.tools import tool
from app.core.rag import (
    audit_collection,
    get_store_history,
    get_database_stats
)
import json


# ============================================================
# TOOL 1 — Compliance Trend Calculator
# ============================================================

@tool
def calculate_compliance_trend(store_name: str) -> str:
    """
    Calculates the compliance score trend for a specific store
    over time. Use this when asked about improvement, decline,
    trends, or score history for a store.
    
    Args:
        store_name: The name of the store to analyze
    """

    history = get_store_history(store_name)

    if not history:
        return f"No audit history found for store: {store_name}"

    if len(history) == 1:
        score = history[0]["metadata"]["compliance_score"]
        date = history[0]["metadata"]["audit_date"]
        return f"Only one audit found for {store_name} on {date} with score {score}/100. Need more audits to calculate trend."

    # Extract scores chronologically (history is newest first, reverse it)
    chronological = list(reversed(history))
    scores = [a["metadata"]["compliance_score"] for a in chronological]
    dates = [a["metadata"]["audit_date"] for a in chronological]

    # Calculate trend
    first_score = scores[0]
    latest_score = scores[-1]
    change = latest_score - first_score
    avg_score = round(sum(scores) / len(scores), 1)

    # Build trend string
    trend_data = "\n".join([
        f"  [{dates[i]}]: {scores[i]}/100"
        for i in range(len(scores))
    ])

    if change > 5:
        trend_direction = f"IMPROVING significantly (+{change} points)"
    elif change > 0:
        trend_direction = f"IMPROVING slightly (+{change} points)"
    elif change == 0:
        trend_direction = "STABLE (no change)"
    elif change > -5:
        trend_direction = f"DECLINING slightly ({change} points)"
    else:
        trend_direction = f"DECLINING significantly ({change} points)"

    return f"""
COMPLIANCE TREND ANALYSIS FOR: {store_name.upper()}
{'='*45}
Total Audits Analyzed: {len(scores)}
First Score: {first_score}/100 ({dates[0]})
Latest Score: {latest_score}/100 ({dates[-1]})
Average Score: {avg_score}/100
Overall Trend: {trend_direction}

Score History (Chronological):
{trend_data}

Analysis: The store has {'improved' if change > 0 else 'declined' if change < 0 else 'maintained'} 
by {abs(change)} points from first to latest audit.
"""


# ============================================================
# TOOL 2 — Worst Performing Zones Finder
# ============================================================

@tool
def get_worst_performing_zones(store_name: str) -> str:
    """
    Analyzes all audits for a store and finds which shelf zones
    fail most frequently. Use this when asked about problem areas,
    worst zones, or which zones need most attention.
    
    Args:
        store_name: The name of the store to analyze
    """

    history = get_store_history(store_name)

    if not history:
        return f"No audit history found for store: {store_name}"

    # Count zone failures across all audits
    zone_failures = {
        "eye_level": 0,
        "golden_zone": 0,
        "top_shelf": 0,
        "bottom_shelf": 0
    }
    zone_total = {k: 0 for k in zone_failures}
    total_audits = len(history)

    for audit in history:
        try:
            analysis_json = audit["metadata"].get("analysis_json", "{}")
            analysis = json.loads(analysis_json)
            zones = analysis.get("zones", {})

            for zone_name, zone_data in zones.items():
                if zone_name in zone_failures:
                    zone_total[zone_name] += 1
                    if zone_data.get("status", "pass").lower() == "fail":
                        zone_failures[zone_name] += 1
        except Exception:
            continue

    # Sort by failure count
    sorted_zones = sorted(
        zone_failures.items(),
        key=lambda x: x[1],
        reverse=True
    )

    result = f"""
ZONE PERFORMANCE ANALYSIS FOR: {store_name.upper()}
{'='*45}
Total Audits Analyzed: {total_audits}

Zone Failure Summary:
"""
    for zone_name, failures in sorted_zones:
        total = zone_total.get(zone_name, total_audits)
        pass_count = total - failures
        failure_rate = round((failures / total * 100), 1) if total > 0 else 0
        status = "🔴 NEEDS ATTENTION" if failures > 0 else "🟢 CONSISTENTLY PASSING"

        result += f"""
  {zone_name.upper().replace('_', ' ')}:
    Failed: {failures}/{total} audits ({failure_rate}% failure rate)
    Passed: {pass_count}/{total} audits
    Status: {status}
"""

    worst = sorted_zones[0]
    if worst[1] > 0:
        result += f"\n⚠️  WORST ZONE: {worst[0].upper().replace('_', ' ')} with {worst[1]} failures"
    else:
        result += "\n✅ All zones passing consistently across all audits!"

    return result


# ============================================================
# TOOL 3 — Audit Summary Generator
# ============================================================

@tool
def generate_audit_summary(store_name: str) -> str:
    """
    Generates a comprehensive formatted audit summary report
    for a store using all available historical data.
    Use this when asked to generate a report, summary, or 
    documentation of audit results.
    
    Args:
        store_name: The name of the store to generate report for
    """

    history = get_store_history(store_name)
    stats = get_database_stats()

    if not history:
        return f"No audit history found for store: {store_name}"

    # Collect all violations across audits
    all_violations = []
    all_brands = set()
    scores = []

    for audit in history:
        meta = audit["metadata"]
        scores.append(meta.get("compliance_score", 0))

        try:
            analysis_json = meta.get("analysis_json", "{}")
            analysis = json.loads(analysis_json)
            all_violations.extend(analysis.get("violations", []))
            all_brands.update(analysis.get("brands_detected", []))
        except Exception:
            continue

    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0

    # Count violation frequency
    violation_counts = {}
    for v in all_violations:
        violation_counts[v] = violation_counts.get(v, 0) + 1

    top_violations = sorted(
        violation_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    summary = f"""
╔══════════════════════════════════════════════════╗
║         COMPREHENSIVE AUDIT SUMMARY REPORT       ║
╚══════════════════════════════════════════════════╝

STORE: {store_name.upper()}
Total Audits Conducted: {len(history)}
Report Generated: {history[0]['metadata'].get('audit_date', 'N/A')} (latest)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Compliance Score : {avg_score}/100
Highest Score Achieved   : {max_score}/100
Lowest Score Recorded    : {min_score}/100
Score Range              : {max_score - min_score} points

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VIOLATION ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Violations Recorded: {len(all_violations)}
"""

    if top_violations:
        summary += "Most Frequent Violations:\n"
        for i, (violation, count) in enumerate(top_violations, 1):
            summary += f"  {i}. ({count}x) {violation}\n"
    else:
        summary += "No violations recorded — Excellent compliance!\n"

    summary += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRANDS MONITORED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{', '.join(sorted(all_brands))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUDIT LOG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for audit in reversed(history):
        meta = audit["metadata"]
        summary += (
            f"  [{meta.get('audit_date')}] "
            f"Score: {meta.get('compliance_score')}/100 | "
            f"Violations: {meta.get('violations_count', 0)} | "
            f"ID: {audit['audit_id']}\n"
        )

    overall = "EXCELLENT" if avg_score >= 90 else "GOOD" if avg_score >= 75 else "NEEDS IMPROVEMENT"
    summary += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERALL ASSESSMENT: {overall}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prepared by: ShelfVision AI Agent
"""
    return summary


# ============================================================
# TOOL 4 — Database Stats
# ============================================================

@tool
def get_all_stores_stats() -> str:
    """
    Returns statistics about all stores in the database.
    Use this when asked about overall performance, all stores,
    or database-wide statistics.
    """

    stats = get_database_stats()

    if stats["total_audits"] == 0:
        return "No audits in database yet."

    return f"""
DATABASE STATISTICS
{'='*35}
Total Audits Stored : {stats['total_audits']}
Stores Tracked      : {', '.join(stats['stores'])}
Average Score       : {stats.get('average_score', 'N/A')}/100
Highest Score       : {stats.get('highest_score', 'N/A')}/100
Lowest Score        : {stats.get('lowest_score', 'N/A')}/100
"""


# All tools exported as a list for the agent
ALL_TOOLS = [
    calculate_compliance_trend,
    get_worst_performing_zones,
    generate_audit_summary,
    get_all_stores_stats
]