from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .concentration import Finding
from .score import Assessment

LABEL = {
    "no_exit_plan": "no exit plan",
    "assurance_stale_or_missing": "SOC 2 / ISO report missing or > 12 months old",
    "recovery_slower_than_our_rto": "their recovery time exceeds our RTO",
    "recovery_unknown": "recovery time unknown",
    "bcp_untested": "no BCP test in the last 12 months",
    "no_right_to_audit": "no right to audit",
    "slow_or_no_incident_notification": "incident notification > 24 h or absent",
    "single_region": "single region",
}
ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def markdown(assessments: list[Assessment], findings: list[Finding], today: date) -> str:
    out = [f"# Third-party resilience assessment ({today.isoformat()})", ""]
    counts = {t: sum(a.tier == t for a in assessments) for t in ORDER}
    out += [" · ".join(f"**{n}** {t}" for t, n in counts.items()), ""]
    out += ["## Concentration risk", ""]
    if findings:
        out += [f"- **{f.kind.replace('_', '-')} `{f.shared}`** carries {len(f.vendors)} critical vendors "
                f"({', '.join(f.vendors)}) supporting {', '.join(f.processes)}" for f in findings]
    else:
        out.append("No shared provider, region or sub-processor across critical vendors.")
    out += ["", "## Vendors by tier", "", "| Tier | Vendor | Service | Inherent | Gaps | Residual | Reassess by |",
            "|---|---|---|---|---|---|---|"]
    for a in sorted(assessments, key=lambda a: (ORDER[a.tier], -a.residual)):
        due = a.reassess_due.isoformat() if a.reassess_due else "never assessed"
        overdue = " ❗" if a.reassess_due and a.reassess_due < today else ""
        out.append(f"| {a.tier} | {a.vendor.name} | {a.vendor.service} | {a.inherent} | {len(a.gaps)} | {a.residual} | {due}{overdue} |")
    out += ["", "## Gaps to close (critical and high)", ""]
    for a in sorted(assessments, key=lambda a: (ORDER[a.tier], -a.residual)):
        if a.tier in ("critical", "high") and a.gaps:
            out.append(f"**{a.vendor.name}**: " + "; ".join(LABEL[g] for g in a.gaps))
            out.append("")
    return "\n".join(out) + "\n"


def write_csv(path: Path, assessments: list[Assessment]) -> None:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["vendor", "service", "criticality", "inherent", "gap_score", "residual", "tier", "gaps", "reassess_due"])
        for a in assessments:
            w.writerow([a.vendor.name, a.vendor.service, a.vendor.criticality, a.inherent, a.gap_score,
                        a.residual, a.tier, ";".join(a.gaps), a.reassess_due or ""])
