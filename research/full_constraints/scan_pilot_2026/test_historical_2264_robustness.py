import unittest
from pathlib import Path
import tempfile
from research.full_constraints.scan_pilot_2026 import historical_2264_robustness as r

class SourceLocked2264LocalRobustnessTests(unittest.TestCase):
    def test_safe_interval_robust_and_no_global_promotion(self):
        with tempfile.TemporaryDirectory() as t:
            v=r.run(Path(t)/"report.json")
        lo,hi=v["eta_below_retained_mu_e_gamma_limit_interval"]
        self.assertLess(lo,v["eta_min"])
        self.assertLess(v["eta_min"],hi)
        self.assertLess(v["retained_mu_e_gamma_partial_BR"],v["MEGII_upper_limit"])
        self.assertEqual(v["original_scalar_vacuum_D10"],"PASS")
        self.assertEqual(v["original_physical_B"],"UNKNOWN")
        self.assertIsNone(v["physics_global_acceptance"])
        self.assertFalse(v["original_production_artifact_full_yukawa_source_binding_revalidated"])
        self.assertFalse(v["new_MG5_generation_executed"])
        self.assertIsNone(v["14TeV_cross_section_pb"])
        self.assertGreater(v["13TeV_LO_cascade_proxy_fb_if_quark_rate_unchanged"],0)

if __name__=="__main__":unittest.main()
