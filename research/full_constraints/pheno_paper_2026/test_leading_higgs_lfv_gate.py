"""Scientific regression tests, not acceptance certificates, for 64 Zee Higgs/LFV cards."""
import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from research.full_constraints.pheno_paper_2026 import leading_higgs_lfv_gate as gate

class ScopedHiggsLFVGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
        cls.source_ids={x["id"] for x in source_points()}
        cls.frozen=Path(__file__).parent
        cls.expected_count=16

    def test_expected_source_metadata_and_bounds(self):
        self.assertEqual(len(self.source_ids),16)
        self.assertAlmostEqual(gate.THRESHOLDS["MEGII_mu_to_e_gamma_90CL"],1.5e-13)
        self.assertAlmostEqual(gate.THRESHOLDS["BelleII_tau_to_3mu_90CL"],1.9e-8)
        self.assertAlmostEqual(gate.THRESHOLDS["ATLAS_h125_to_mutau_95CL"],0.0018)

    def test_aggregator_fail_closed_for_fabricated_full_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            r={"n_evaluated":64,"full_Higgs":"PASS",
               "full_LFV":"UNKNOWN","global_acceptance":None,"families":[]}
            f=Path(td)/"invalid.json";f.write_text(json.dumps(r))
            with self.assertRaises(ArithmeticError):
                gate.evaluate(f,Path(td)/"out.json")

    def test_partial_amplitude_cannot_be_treated_as_complete_physical_lfv(self):
        text=Path(__file__).with_name("leading_higgs_lfv_gate.py").read_text()
        for physically_required in (
            '"full_mu3e_one_loop_executed":False',
            '"full_mu_e_conversion_executed":False',
            '"full_Zee_mixed_two_loop_LFV_executed":False',
            '"physical_Higgs":"UNKNOWN"',
            '"physical_LFV":"UNKNOWN"',
            '"global_acceptance":None',
            '"Al_conversion_full_one_loop":None',
        ):
            self.assertIn(physically_required,text)

if __name__=="__main__":
    unittest.main()
