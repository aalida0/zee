"""A1S 2026 Misiak et al Eq.(4) Wilson-level Zee scalar-sector screen."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1s_run_modern_2026_screen import (
    SOURCE,PDG_EXP,MODERN_SM,K7,K8,MU0_GEV,
    weights,linearized_2026,combine,parse_probe,report,
)

def pt(m,dc7,dc8):
    return {"mass_GeV":m,"matching_scale_GeV":160.,
            "delta_C7_LO":dc7,"delta_C8_LO":dc8,
            "running_mt_mu0_GeV":163.,
            "tanbeta":5.597170833164245}

def fake_points():
    return {300.:pt(300.,-.07,-.03),
            670.:pt(670.,-.03,-.01),
            700.:pt(700.,-.025,-.012),
            1000.:pt(1000.,-.017,-.008),
            2000.:pt(2000.,-.008,-.003)}

def raw_output(m=700.,tan=5.597170833164245,mu=160.,
               c7=-.04,c8=-.02):
    return (
        "STATUS A1S_SOURCE_PINNED_LO_MATCHING_NO_BR_OR_EXCLUSION\n"
        f"INPUT mH_GeV={m:.17g} tanbeta={tan:.17g} "
        f"mu0_GeV={mu:.17g} running_mt_mu0_GeV=163.0\n"
        f"DELTA_C7_LO={c7:.17g}\nDELTA_C8_LO={c8:.17g}\n"
        "NO_THEORY_LIKELIHOOD_VALIDATED true\n"
    )

class TestModern2026LinearizedScreen(unittest.TestCase):
    def test_original_2026_paper_formula_exact(self):
        self.assertIn("2608.29863",SOURCE)
        x=linearized_2026(-.01,-.02)
        self.assertAlmostEqual(x["linearized_shift_times_1e4"],
                               .0851+.0432)
        self.assertAlmostEqual(x["linearized_predicted_central_times_1e4"],
                               3.54+.1283)
        self.assertEqual(MU0_GEV,160.)
        self.assertEqual(MODERN_SM["central_times_1e4"],3.54)
        self.assertEqual(PDG_EXP["central_times_1e4"],3.49)

    def test_endpoint_gamma_zero_and_pi2_restore_exact_one_state(self):
        light=pt(300.,-.05,-.03)
        heavy=pt(700.,-.012,-.007)
        l=combine(light,heavy,0.)
        h=combine(light,heavy,math.pi/2)
        self.assertAlmostEqual(l["LO_delta_C7_mu0_160"],-.05,places=14)
        self.assertAlmostEqual(l["LO_delta_C8_mu0_160"],-.03,places=14)
        self.assertAlmostEqual(h["LO_delta_C7_mu0_160"],-.012,places=14)
        self.assertAlmostEqual(h["LO_delta_C8_mu0_160"],-.007,places=14)
        self.assertFalse(l["weighted_BR_of_single_Higgs_states"])

    def test_degenerate_states_rotation_independent(self):
        p=pt(700.,-.012,-.008)
        for g in (0.,.1,1.089,math.pi/2):
            x=combine(p,p,g)
            self.assertAlmostEqual(x["LO_delta_C7_mu0_160"],-.012)
            self.assertAlmostEqual(x["LO_delta_C8_mu0_160"],-.008)

    def test_linearized_formula_is_affine_not_weighted_squares(self):
        light=pt(300.,-.08,-.04)
        heavy=pt(700.,-.02,-.01)
        result=combine(light,heavy,1.089)
        w1,w2=weights(1.089)
        self.assertAlmostEqual(result["LO_delta_C7_mu0_160"],
                               w1*(-.08)+w2*(-.02))
        self.assertAlmostEqual(result["LO_delta_C8_mu0_160"],
                               w1*(-.04)+w2*(-.01))
        self.assertAlmostEqual(result["linearized_shift_times_1e4"],
                               K7*result["LO_delta_C7_mu0_160"]+
                               K8*result["LO_delta_C8_mu0_160"])
        self.assertTrue(result["quadratic_NP_terms_omitted"])

    def test_wrong_mu0_rejected_not_fixed_by_legacy_input(self):
        with self.assertRaisesRegex(ValueError,"2026 Eq4 contract"):
            parse_probe(raw_output(mu=160.7384),700.,
                        5.597170833164245)

    def test_real_source_print_contract_and_nonfinite_block(self):
        x=parse_probe(raw_output(),700.,5.597170833164245)
        self.assertAlmostEqual(x["delta_C7_LO"],-.04)
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            parse_probe(raw_output().replace("DELTA_C7_LO=-0.040000000000000001",
                                              "DELTA_C7_LO=1e999"),700.,
                        5.597170833164245)
        with self.assertRaisesRegex(ValueError,"Missing/duplicate"):
            parse_probe(raw_output()+ "DELTA_C8_LO=-.02\n",
                        700.,5.597170833164245)

    def test_two_state_screen_never_excludes(self):
        points=fake_points()
        result=report(points,300.,700.,1.089,5.597170833164245,{})
        self.assertIn("NOT_EXCLUSION",result["status"])
        self.assertEqual(result["full_2026_single_TypeII_95CL_lower_mass_GeV"],
                         670.)
        self.assertFalse(result["full_2026_NNLO_observable_kernel_reimplemented"])
        self.assertFalse(result["linearized_approximation_assessed_for_LARGE_NP"])
        self.assertFalse(result["Zee_two_state_full_BR_validated"])
        self.assertFalse(result["experimental_95CL_likelihood_validated"])
        self.assertIsNone(result["Zee_benchmark_allowed"])
        self.assertIsNone(result["Zee_benchmark_excluded"])

    def test_omit_670_paper_control_blocks(self):
        points=fake_points();points.pop(670.)
        with self.assertRaisesRegex(ValueError,"Missing current benchmark"):
            report(points,300.,700.,1.089,5.597170833164245,{})

    def test_mass_order_and_gamma_range_enforced(self):
        points=fake_points()
        with self.assertRaisesRegex(ValueError,"ordered"):
            report(points,700.,300.,1.089,5.597170833164245,{})
        with self.assertRaisesRegex(ValueError,"gamma"):
            combine(points[300.],points[700.],-1.)
        with self.assertRaisesRegex(ValueError,"gamma"):
            combine(points[300.],points[700.],math.pi)

    def test_nonfinite_wilson_values_rejected(self):
        for bad in (float("nan"),float("inf"),-float("inf")):
            with self.assertRaisesRegex(ValueError,"Nonfinite"):
                linearized_2026(bad,0.)

if __name__=="__main__":
    unittest.main()
