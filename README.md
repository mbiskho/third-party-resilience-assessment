# Third-Party Resilience Assessment

Our recovery plans are only as good as the vendors under them. This tool keeps a register of third parties and scores each one on how much we depend on them against how prepared they and we are for them to fail. It also finds concentration risk: several critical services quietly resting on the same provider or region.

```
vendors.yaml ──► inherent risk (criticality × data × substitutability)
                 × control gaps (no exit plan, stale SOC 2, no tested BCP, SLA below our RTO …)
             ──► residual score → tier (critical / high / medium / low) → reassessment frequency
             ──► concentration findings (provider, region, sub-processor shared by critical services)
             ──► report.md + register.csv
```

## What counts against a vendor

| Gap | Why it matters |
|---|---|
| No documented exit plan | if they fail or we must leave, we start from zero |
| SOC 2 / ISO report older than 12 months | the assurance no longer covers today's controls |
| Their recovery time is longer than our RTO for the processes using them | our targets are fiction while they're in the path |
| No BCP test evidence | a plan they've never tested |
| No contractual right to audit, or no incident-notification clause | we find out last, and can't verify |
| Single region, or one sub-processor for everything | one event takes them out completely |

## Usage

```bash
pip install -e ".[dev]"
vendorrisk assess examples/vendors.yaml --out out/
# out/report.md: tiers, top gaps per vendor, concentration findings, reassessments due
# out/register.csv: for the GRC tool
```

## Layout

```
vendorrisk/model.py    vendor schema + validation
vendorrisk/score.py    inherent risk, control gaps, residual score, tiering (pure functions)
vendorrisk/concentration.py   shared provider / region / sub-processor across critical services
vendorrisk/report.py   Markdown + CSV
vendorrisk/cli.py      `vendorrisk assess`
examples/vendors.yaml  a cloud provider, a KYC vendor, a card processor, an SMS gateway, and more
```
