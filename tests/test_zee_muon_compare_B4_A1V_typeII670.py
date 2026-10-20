"""Paper2 same-scheme A1V single-TypeII670 comparator fail-closed tests."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_muon_compare_B4_A1V_typeII670 import (
    STATUS,identity,combine,compare,summarize
)

def point(ident="B4_1",g=1.1):
    return {
        "id":ident,"candidate_status":"SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED",
        "mH1":"300","mH2":"700","gamma":str(g),"tanbeta":"4",
        "BR_H2_H1Z_nonleptonic_included_upper_proxy":".8",
        "BR_H1_tb_nonleptonic_included_upper_proxy":".9",
    }

def flavor(p,delta=5e-5,sm=3.382458e-4):
    return {
        **{k:p[k] for k in ("mH1","mH2","gamma","tanbeta")},
        "SM_BR":sm,"full_Zee_BR":sm+delta,
        "linear_delta_BR":delta*.95,
        "quadratic_delta_BR":delta*.05,
    }

def ref(t,delta=4e-5,sm=3.382458e-4):
    return {"SM_BR":sm,"full_Zee_BR":sm+delta}


class TestZeeCompareTypeII670(unittest.TestCase):
    def test_do_not_pretend_legacy_is_physical_exclusion(self):
        self.assertIn("NOT_MODEL_EXCLUSION",STATUS)

    def test_known_control_ratio_and_truth_decay_count(self):
        p=point()
        r=combine(p,flavor(p),ref(4))
        self.assertAlmostEqual(r["R_legacy_Zee_over_TypeII670"],1.25,
                               delta=1e-11)
        self.assertFalse(r["ratio_below_1_not_physical_acceptance"])
        self.assertGreater(r["sigma_Z_both_charges_1500_fb"],0)
        self.assertAlmostEqual(
            r["Zll_tb_tb_included_channel_truth_ceiling_1500_0p5ab"],
            r["sigma_Z_both_charges_1500_fb"]*500*.8*.9*.9*.0673,
            delta=1e-10)

    def test_detect_r_below_one_without_adding_exclusion(self):
        p=point()
        r=combine(p,flavor(p,delta=3e-5),ref(4))
        self.assertAlmostEqual(r["R_legacy_Zee_over_TypeII670"],.75,
                               delta=1e-12)
        self.assertTrue(r["ratio_below_1_not_physical_acceptance"])
        x=summarize([r])
        self.assertEqual(x["n_ratio_below_1_NOT_allowed_count"],1)
        self.assertFalse(x["full_neutrino_LFV_HiggsTools_modern_NNLO_completed"])

    def test_refuses_unmatched_B4_and_A1V_rows(self):
        p=point()
        f=flavor(p)
        f["mH2"]="701"
        with self.assertRaisesRegex(ValueError,"row identity"):
            identity(p,f)
        with self.assertRaisesRegex(ValueError,"row identity"):
            combine(p,f,ref(4))

    def test_refuses_SM_baseline_mismatch(self):
        p=point()
        with self.assertRaisesRegex(ValueError,"SM baseline"):
            combine(p,flavor(p),ref(4,sm=3.6e-4))

    def test_refuses_inconsistent_linear_and_quadratic_terms(self):
        p=point()
        f=flavor(p)
        f["quadratic_delta_BR"]=0.0
        with self.assertRaisesRegex(ValueError,"decomposition"):
            combine(p,f,ref(4))

    def test_refuses_nonpositive_or_nonfinite_reference_shift(self):
        p=point()
        for d in (0.,-1e-5,math.nan):
            with self.subTest(d=d):
                with self.assertRaisesRegex(ValueError,"670-GeV"):
                    combine(p,flavor(p),ref(4,delta=d))

    def test_correct_selection_and_same_tanbeta_parameter(self):
        p1=point("B4_1",1.1)
        p2=point("B4_2",1.2)
        calls=[]
        def reference(t):
            calls.append(t)
            return ref(t)
        rows=compare([p1,p2],[flavor(p1),flavor(p2)],
                     reference,progress_every=0)
        self.assertEqual(len(rows),2)
        self.assertEqual(calls,[4.,4.])
        self.assertEqual(summarize(rows)["n_ratio_at_or_above_1_NOT_excluded_count"],2)

    def test_missing_duplicate_or_mislabeled_B4_rejected(self):
        p=point()
        p["candidate_status"]="ALLOWED"
        with self.assertRaisesRegex(ValueError,"screened provenance"):
            identity(p,flavor(p))
        p1=point()
        with self.assertRaisesRegex(ValueError,"duplicated"):
            compare([p1,p1],[flavor(p1),flavor(p1)],ref,0)
        with self.assertRaisesRegex(ValueError,"rows differ"):
            compare([p1],[],ref,0)


if __name__=="__main__":
    unittest.main()
