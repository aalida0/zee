#!/usr/bin/env python3
"""F13: real scalar/EWPO tests with synthetic Wilson source (NOT physical flavor)."""
import math,sys,unittest
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"scripts"))
import zee_paper1_F13_heavy_flavor_aware_final_scan as q
from zee_paper1_F13_heavy_P1_seeds import validated_p1_seeds
def fake_source(m,t):
    return dict(mass_GeV=m,tanbeta=t,matching_scale_GeV=160.,
       delta_C7_LO=-.042*(670./m)**2,delta_C8_LO=-.019*(670./m)**2)
class TestF13(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seeds,cls.proof=validated_p1_seeds(160,40,20261021,max_seeds=3)
    def test_heavy_scalar_EWPO_seeds(self):
        self.assertGreaterEqual(len(self.seeds),2)
        self.assertTrue(self.proof["all_are_genuine_rebuilt_theory_EWPO_not_allowed"])
        for p,r in self.seeds:
            self.assertTrue(q.domain(p))
            self.assertEqual(r["candidate_status"],"SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED")
    def test_48_actual_scalar_EWPO_proposals_and_synthetic_flavor(self):
        rows,s=q.walk(self.seeds,48,40,np.random.default_rng(44),fake_source,report_every=0)
        self.assertGreaterEqual(len(rows),len(self.seeds))
        self.assertEqual(s["new_proposals"],48)
        self.assertGreaterEqual(s["flavor_benchmark_backend_calls"],3)
        for x in rows:
            self.assertIsNone(x["fully_allowed_Zee_model"])
            self.assertIsNone(x["modern_2026_full_NNLO_excluded_or_allowed"])
            self.assertTrue(550<=x["mH1"]<=720)
            self.assertGreater(x["mH2"]-x["mH1"],q.MZ)
        arr,hit=q.pick(rows,min(4,len(rows)))
        self.assertEqual(len({r["id"] for r in arr}),len(arr))
    def test_matching_weights(self):
        p=self.seeds[0][0];v=q.screen_flavor(p,fake_source,{})
        w=math.cos(p["gamma"])**2;t=math.tan(p["beta"])
        d1=fake_source(p["mH1"],t)["delta_C7_LO"]
        d2=fake_source(p["mH2"],t)["delta_C7_LO"]
        self.assertAlmostEqual(v["delta_C7_LO"],w*d1+(1-w)*d2)
        self.assertAlmostEqual(v["2026_Eq4_LO_linearized_BRx1e4"],
           3.54-8.51*v["delta_C7_LO"]-2.16*v["delta_C8_LO"])
    def test_pick_priority(self):
        rows=[dict(id="A",mH1=610,mH2=870,gamma=.9,
             production_weighted_nonleptonic_cascade_upper_proxy=.4,
             abs_z_illustrative_NOT_CL=2.8,diagnostic_below_1p96_NOT_allowed=False),
              dict(id="B",mH1=650,mH2=940,gamma=.8,
             production_weighted_nonleptonic_cascade_upper_proxy=.35,
             abs_z_illustrative_NOT_CL=1.8,diagnostic_below_1p96_NOT_allowed=True)]
        r,hit=q.pick(rows,2);self.assertTrue(hit);self.assertEqual(r[0]["id"],"B")
        rows[1]["diagnostic_below_1p96_NOT_allowed"]=False
        _,hit=q.pick(rows,2);self.assertFalse(hit)
    def test_domain_invalid(self):
        p=dict(self.seeds[0][0]);p["mH1"]=499;self.assertFalse(q.domain(p))
        p["mH1"]=600;p["mH2"]=690;self.assertFalse(q.domain(p))
        p["mH2"]=1800;self.assertFalse(q.domain(p))
    def test_actual_heavy_seed_complex_neutrino_and_partial_LFV_widths(self):
        # This is actual Zee neutrino and subset-LFV code at an actual
        # scalar/EWPO screened heavy point; not synthetic neutrino data.
        # The A1S/2026 matching calculation itself is tested separately.
        p,r=self.seeds[0]
        row=q.augment(r,p,fake_source,{})
        results=q.fit_priorities([row],np.random.default_rng(555),
                      trials=20,local_seeds=2,maxfev=80)
        result=results[row["id"]]
        print("F13_HEAVY_COMPLEX_NEUTRINO_LFV_SMOKE",
              row["id"],result["status"],result.get("best",{}).get(
                  "score_partial_LFV_max_ratio_NOT_Full_CL"))
        self.assertIn(result["status"],(
            "NEUTRINO_EXACT_WITH_PARTIAL_LFV_AND_INCLUDED_CASCADE_ONLY",
            "NO_NEUTRINO_CLOSED_TRIALS_FOUND_NOT_EXCLUSION",
            "ALL_LOCAL_OPTIMIZATIONS_INVALID_NOT_EXCLUSION"))
        self.assertIsNone(result["model_allowed_or_excluded"])
        if "best" in result:
            self.assertLess(result["best"]["neutrino_matrix_closure_eV"],1e-9)
            self.assertIsNone(result["best"]["fully_Zee_allowed_or_excluded"])
    def test_no_allowed(self):
        self.assertIn("NOT_ALLOWED",q.STATUS)
        self.assertTrue(any("2026" in a for a in q.MISSING))
        self.assertTrue(any("pb" in a for a in q.MISSING))
if __name__=="__main__":unittest.main()
