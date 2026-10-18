from datetime import date

from vendorrisk.concentration import find
from vendorrisk.model import Vendor
from vendorrisk.score import assess, control_gaps, inherent_risk

TODAY = date(2026, 10, 18)


def vendor(**kw):
    base = dict(name="v", service="s", supports=["p"], criticality=3, data_access="internal", substitutability="months",
                our_rto_hours=4, vendor_recovery_hours=2, exit_plan=True, assurance_report_date=date(2026, 6, 1),
                bcp_tested_date=date(2026, 5, 1), right_to_audit=True, incident_notification_hours=24,
                regions=["a", "b"])
    return Vendor(**{**base, **kw})


def test_well_controlled_vendor_has_no_gaps():
    assert control_gaps(vendor(), TODAY) == []
    assert assess(vendor(), TODAY).residual == 0


def test_recovery_slower_than_our_rto_is_a_gap():
    assert "recovery_slower_than_our_rto" in control_gaps(vendor(vendor_recovery_hours=8), TODAY)
    assert "recovery_unknown" in control_gaps(vendor(vendor_recovery_hours=None), TODAY)


def test_stale_assurance():
    assert "assurance_stale_or_missing" in control_gaps(vendor(assurance_report_date=date(2025, 6, 1)), TODAY)


def test_critical_vendor_never_below_high():
    assert assess(vendor(criticality=5), TODAY).tier == "high"     # perfect controls still high
    poor = vendor(criticality=5, data_access="sensitive", substitutability="hard", exit_plan=False, regions=["a"],
                  assurance_report_date=None, vendor_recovery_hours=None)
    assert assess(poor, TODAY).tier == "critical"


def test_inherent_weights():
    assert inherent_risk(vendor(criticality=5, data_access="sensitive", substitutability="hard")) == 5.0


def test_concentration_on_shared_provider_and_region():
    vs = [vendor(name="A", criticality=5, hosted_on="aws", regions=["x"]),
          vendor(name="B", criticality=4, hosted_on="AWS", regions=["x"]),
          vendor(name="C", criticality=2, hosted_on="aws", regions=["x"])]   # not critical: ignored
    kinds = {(f.kind, f.shared): f.vendors for f in find(vs)}
    assert kinds[("provider", "aws")] == ["A", "B"]
    assert kinds[("region", "x")] == ["A", "B"]
