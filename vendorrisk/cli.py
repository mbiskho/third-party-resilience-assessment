from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import concentration
from .model import load
from .report import markdown, write_csv
from .score import assess


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="vendorrisk")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("assess")
    p.add_argument("vendors", type=Path)
    p.add_argument("--out", type=Path, default=Path("out"))
    a = ap.parse_args(argv)

    today = date.today()
    vendors = load(a.vendors)
    assessments = [assess(v, today) for v in vendors]
    findings = concentration.find(vendors)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "report.md").write_text(markdown(assessments, findings, today))
    write_csv(a.out / "register.csv", assessments)
    crit = sum(x.tier == "critical" for x in assessments)
    print(f"{len(vendors)} vendors, {crit} critical, {len(findings)} concentration findings → {a.out}/report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
