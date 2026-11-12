"""Zee scalar threshold/width materiality classification regression."""
import copy,unittest
from research.full_constraints.pheno_paper_2026.width_threshold_audit_64 import diagnostics

class ThresholdAuditUnit(unittest.TestCase):
    def fixture(self):
        p={"mH1":700.,"mH2":1300.,"mh2":1250.,"ma":1180.}
        charge={"H1":{"total":{"total_width_GeV":13.}},
                "H2":{"total":{"total_width_GeV":40.}}}
        H={"mixed_order_known_channel_sum_GeV":69.}
        A={"mixed_order_known_channel_sum_GeV":55.}
        return p,charge,H,A

    def test_far_cascades_and_width_ratios(self):
        p,c,h,a=self.fixture()
        d=diagnostics(p,c,h,a)
        self.assertAlmostEqual(d["source_width_floor_over_mass"]["H"],69/1250.)
        self.assertEqual(d["thresholds"]["H2 -> H1 Z"]["classification"],
                         "OPEN_FAR_ABOVE_THRESHOLD_5WIDTHS")
        self.assertTrue(d["all_open_H1W_and_H2H1Z_far_five_widths"])
        self.assertIsNone(d["inferred_narrow_width_allowed"])
        self.assertEqual(d["ttpair_resonance_interference_status"],"MISSING_CALCULATION")

    def test_nearby_open_threshold_flagged_as_unknown(self):
        p,c,h,a=self.fixture()
        p["mH2"]=800.
        d=diagnostics(p,c,h,a)
        self.assertEqual(d["thresholds"]["H2 -> H1 Z"]["classification"],
                         "OPEN_NEAR_THRESHOLD_NEEDS_OFFSHELL_CHECK")
        self.assertFalse(d["all_open_H1W_and_H2H1Z_far_five_widths"])

    def test_broad_known_width_floor_and_negative_rejected(self):
        p,c,h,a=self.fixture()
        h["mixed_order_known_channel_sum_GeV"]=300
        d=diagnostics(p,c,h,a)
        self.assertTrue(d["known_width_floor_exceeds_10pct"]["H"])
        c["H2"]["total"]["total_width_GeV"]=-1
        with self.assertRaises(ValueError):diagnostics(p,c,h,a)

if __name__=="__main__":unittest.main()
