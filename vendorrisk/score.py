from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .model import DATA, SUBST, Vendor

# weight of each control gap (points added to a 0-10 gap score, capped)
GAP_WEIGHTS = {
    "no_exit_plan": 2.0,
    "assurance_stale_or_missing": 2.0,
    "recovery_slower_than_our_rto": 2.5,
    "recovery_unknown": 1.5,
    "bcp_untested": 1.5,
    "no_right_to_audit": 0.5,
    "slow_or_no_incident_notification": 1.0,
    "single_region": 1.0,
}
REASSESS_DAYS = {"critical": 180, "high": 365, "medium": 730, "low": 1095}


@dataclass
class Assessment:
    vendor: Vendor
    inherent: float          # 1..5
    gaps: list[str]
    gap_score: float         # 0..10
    residual: float          # 0..50
    tier: str
    reassess_due: date | None


def inherent_risk(v: Vendor) -> float:
    """How much we depend on them, ignoring controls. Criticality dominates."""
    return round(0.5 * v.criticality + 0.25 * DATA[v.data_access] + 0.25 * SUBST[v.substitutability], 2)


def control_gaps(v: Vendor, today: date) -> list[str]:
    g = []
    if not v.exit_plan:
        g.append("no_exit_plan")
    if v.assurance_report_date is None or (today - v.assurance_report_date).days > 365:
        g.append("assurance_stale_or_missing")
    if v.vendor_recovery_hours is None:
        g.append("recovery_unknown")
    elif v.vendor_recovery_hours > v.our_rto_hours:
        g.append("recovery_slower_than_our_rto")
    if v.bcp_tested_date is None or (today - v.bcp_tested_date).days > 365:
        g.append("bcp_untested")
    if not v.right_to_audit:
        g.append("no_right_to_audit")
    if v.incident_notification_hours is None or v.incident_notification_hours > 24:
        g.append("slow_or_no_incident_notification")
    if len(v.regions) < 2:
        g.append("single_region")
    return g


def tier_for(residual: float, criticality: int) -> str:
    # A vendor that stops a process is never below "high", whatever its controls.
    if residual >= 30 or (criticality == 5 and residual >= 15):
        return "critical"
    if residual >= 15 or criticality >= 4:
        return "high"
    if residual >= 6:
        return "medium"
    return "low"


def assess(v: Vendor, today: date) -> Assessment:
    inh = inherent_risk(v)
    gaps = control_gaps(v, today)
    gap_score = min(10.0, sum(GAP_WEIGHTS[g] for g in gaps))
    residual = round(inh * gap_score, 1)
    tier = tier_for(residual, v.criticality)
    due = None
    if v.last_assessed:
        from datetime import timedelta
        due = v.last_assessed + timedelta(days=REASSESS_DAYS[tier])
    return Assessment(v, inh, gaps, gap_score, residual, tier, due)
