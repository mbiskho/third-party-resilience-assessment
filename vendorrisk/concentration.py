from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .model import Vendor


@dataclass
class Finding:
    kind: str           # provider | region | sub_processor
    shared: str
    vendors: list[str]
    processes: list[str]


def find(vendors: list[Vendor], min_criticality: int = 4) -> list[Finding]:
    """Something shared by two or more critical vendors is a single point of failure we don't control."""
    critical = [v for v in vendors if v.criticality >= min_criticality]
    groups: dict[tuple[str, str], list[Vendor]] = defaultdict(list)
    for v in critical:
        if v.hosted_on:
            groups[("provider", v.hosted_on.lower())].append(v)
        if len(v.regions) == 1:  # multi-region vendors don't concentrate on one region
            groups[("region", v.regions[0].lower())].append(v)
        for sp in v.sub_processors:
            groups[("sub_processor", sp.lower())].append(v)
    out = [Finding(kind, shared, sorted(x.name for x in vs), sorted({p for x in vs for p in x.supports}))
           for (kind, shared), vs in groups.items() if len(vs) >= 2]
    return sorted(out, key=lambda f: (-len(f.vendors), f.kind, f.shared))
