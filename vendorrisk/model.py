from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml


@dataclass
class Vendor:
    name: str
    service: str
    supports: list[str]                # business processes that depend on this vendor
    criticality: int                   # 1 (nice to have) .. 5 (process stops without it)
    data_access: str                   # none | internal | personal | sensitive
    substitutability: str              # easy | months | hard
    our_rto_hours: float               # strictest RTO of the processes it supports (from the BIA)
    vendor_recovery_hours: float | None = None   # their stated RTO; None = unknown
    exit_plan: bool = False
    assurance_report_date: date | None = None    # SOC 2 Type II / ISO 27001 certificate
    bcp_tested_date: date | None = None
    right_to_audit: bool = False
    incident_notification_hours: float | None = None
    regions: list[str] = field(default_factory=list)
    hosted_on: str | None = None       # their infrastructure provider, e.g. "aws"
    sub_processors: list[str] = field(default_factory=list)
    last_assessed: date | None = None


DATA = {"none": 1, "internal": 2, "personal": 4, "sensitive": 5}
SUBST = {"easy": 1, "months": 3, "hard": 5}


def load(path: str | Path) -> list[Vendor]:
    vendors = [Vendor(**v) for v in yaml.safe_load(Path(path).read_text())["vendors"]]
    for v in vendors:
        if not 1 <= v.criticality <= 5:
            raise ValueError(f"{v.name}: criticality must be 1-5")
        if v.data_access not in DATA:
            raise ValueError(f"{v.name}: data_access must be one of {list(DATA)}")
        if v.substitutability not in SUBST:
            raise ValueError(f"{v.name}: substitutability must be one of {list(SUBST)}")
    return vendors
