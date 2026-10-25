#!/usr/bin/env python3
"""Synthetic source adapter tests for F12 physical 309-row Eq4 screening.
No synthetic data is real Zee phenomenology.
"""
import math,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"scripts"))
import zee_paper1_F12_309_modern_Eq4_Bsgamma_frontier as f

def sample(n=309):
    source={}
    for i in range(n):
        id=f"B4_original_{i:04d}"
        source[id]={
           "mH1_GeV":230+0.5*i,"mH2_GeV":800+1.2*i,
           "gamma":1.05,"tanbeta":5.6,
           "E7_included_cascade_proxy_NOT_physical_rate":.4+.0002*i,
           "HiggsSignals_E6_delta_chi2_NOT_CL":1.,
           "BR_BtoXsgamma_legacy_SuperIso_two_state":.00039,
        }
    return source
def fake_probe(_binary,m,t):
    return {"mass_GeV":m,"tanbeta":t,
            "delta_C7_LO":-.07*(500./m)**2,
            "delta_C8_LO":-.03*(500./m)**2,
            "matching_scale_GeV":160.}
class TestF12(unittest.TestCase):
    def test_modern_author_formula(self):
        q=f.linearized_2026(-.05,-.03)
        self.assertAlmostEqual(q["linearized_predicted_central_times_1e4"],
                               3.54+8.51*.05+2.16*.03)
        self.assertTrue(q["quadratic_NP_terms_omitted"])
    def test_all_309_and_source_caching(self):
        rows,m=f.evaluate(sample(),None,probe=fake_probe)
        self.assertEqual(len(rows),309)
        self.assertEqual(len({r["candidate_id"] for r in rows}),309)
        self.assertEqual(m["unique_source_probes"],619)
        for r in rows:
            self.assertIsNone(r["F12_full_Zee_allowed_or_excluded"])
            self.assertIsNone(r["F12_modern_2026_full_NNLO_Zee_BR"])
            self.assertFalse(r["model_theory_covariance_calibrated"])
            self.assertGreater(r["2026_published_Eq4_LO_linear_BRx1e4"],3.54)
            self.assertGreater(r["Zee_to_TypeII670_Eq4_LO_shift_ratio_NOT_CL"],0)
    def test_frontier_non_dominated(self):
        rows=[dict(candidate_id="A",E7_included_cascade_proxy_NOT_physical_pb=.8,
                  **{"2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL":3.}),
              dict(candidate_id="B",E7_included_cascade_proxy_NOT_physical_pb=.75,
                  **{"2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL":2.}),
              dict(candidate_id="C",E7_included_cascade_proxy_NOT_physical_pb=.73,
                  **{"2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL":2.6}),
              dict(candidate_id="D",E7_included_cascade_proxy_NOT_physical_pb=.69,
                  **{"2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL":1.5})]
        answer=f.frontier(rows)
        self.assertEqual([v["candidate_id"] for v in answer],["A","B","D"])
    def test_cannot_import_source_outside_domain(self):
        x=sample(n=1)
        x["B4_original_0000"]["gamma"]=math.pi
        with self.assertRaises(ValueError):
            f.evaluate(x,None,probe=fake_probe)
    def test_read_f6_has_unvalidated_status(self):
        self.assertIn("NOT_EXCLUSION",f.STATUS)
        self.assertTrue(any("NNLO" in x for x in f.MISSING))
if __name__=="__main__":unittest.main()
