"""Gate A1T: check A1R/A1S actual outputs without fake 95% flavour exclusions."""
from __future__ import annotations
from copy import deepcopy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1t_check_2026_screen_vs_legacy_shifts import assess

TAN=5.597170833164245
SM_V5=.0003382457724
VENDOR={
    300:.00045115303105,
    700:.00037793429732,
    1000:.00036207866737,
    2000:.00034638266593,
}
PROBES={
    300:(-.116249118178,-.11298942148),
    670:(-.0461729790719,-.0514806431451),
    700:(-.0436165310583,-.0489292812783),
    1000:(-.0268581378129,-.0315087201513),
    2000:(-.00958410462722,-.0119866333575),
}
GAMMA=1.089

def realistic_fixtures():
    old={
        "status":"GATE_A1R_SINGLE_TYPEII_OBSERVABLE_BR_PILOT_"
                 "AWAITING_INDEPENDENT_ERROR_BUDGET",
        "SM_model_BR":SM_V5,
        "TypeII_control_points":{
            f"TypeII{mass}":{
                "mH_GeV":float(mass),
                "tanbeta":TAN,
                "BR_B_to_Xs_gamma":br,
            } for mass,br in VENDOR.items()
        },
    }
    w1=math.cos(GAMMA)**2
    w2=math.sin(GAMMA)**2
    p7=w1*PROBES[300][0]+w2*PROBES[700][0]
    p8=w1*PROBES[300][1]+w2*PROBES[700][1]
    shift=-8.51*p7-2.16*p8
    new={
        "status":"GATE_A1S_2026_MODERN_EQ4_LO_LINEARIZED_ZEE_SCREEN_NOT_EXCLUSION",
        "Eq4_coefficients":{
            "constant":3.54,"coefficient_delta_C7":-8.51,
            "coefficient_delta_C8":-2.16,
            "matching_scale_GeV":160.,
        },
        "SM_2026":{"central_times_1e4":3.54},
        "experimental_PDG_2026":{"central_times_1e4":3.49},
        "source_pinned_LO_coefficients":{
            str(float(mass)):{
                "mass_GeV":float(mass),
                "tanbeta":TAN,
                "matching_scale_GeV":160.,
                "delta_C7_LO":c7,
                "delta_C8_LO":c8,
            } for mass,(c7,c8) in PROBES.items()
        },
        "selected_Zee_scalar_sector_benchmark":{
            "mH1_GeV":300.,"mH2_GeV":700.,
            "w_light_cos2":w1,"w_heavy_sin2":w2,
            "linearized_shift_times_1e4":shift,
            "linearized_predicted_central_times_1e4":3.54+shift,
        },
    }
    return old,new

class TestGateA1T(unittest.TestCase):
    def test_actual_printed_benchmark_numbers_reproduced(self):
        old,new=realistic_fixtures()
        r=assess(old,new)
        self.assertIn("NOT_PRECISION_OR_EXCLUSION",r["status"])
        z=r["Zee_screen"]
        self.assertAlmostEqual(z["2026_Eq4_LO_BR_times_1e4"],
                               4.17928885635,places=9)
        self.assertAlmostEqual(z["illustrative_naive_uncorrelated_pull_sigma"],
                               2.920610618,places=7)
        bymass={x["mass_GeV"]:x for x in r["single_state_diagnostics"]}
        self.assertAlmostEqual(bymass[700]["A1R_legacy_BR_shift_times_1e4"],
                               .3968852492,places=9)
        self.assertAlmostEqual(
            bymass[700]["A1S_2026_linearized_LO_BR_shift_times_1e4"],
            .47686392687,places=9)

    def test_no_user_facing_exclusion_or_covariance_from_diagnostic(self):
        a,b=realistic_fixtures()
        r=assess(a,b)
        self.assertIsNone(r["Zee_allowed"])
        self.assertIsNone(r["Zee_excluded"])
        self.assertFalse(r["mixed_state_full_2026_NNLO_BR_measured"])
        self.assertFalse(r["model_specific_theory_uncertainty_quantified"])
        self.assertFalse(r["experimental_likelihood_validated"])
        self.assertTrue(r["Zee_screen"][
            "weighted_legacy_shift_NOT_a_physical_two_state_BR"])
        self.assertTrue(r["Zee_screen"][
            "pull_not_a_95CL_exclusion_significance"])

    def test_wrong_eq4_scale_blocked(self):
        a,b=realistic_fixtures()
        b["Eq4_coefficients"]["matching_scale_GeV"]=160.7384
        with self.assertRaisesRegex(ValueError,"Eq4 scale"):
            assess(a,b)

    def test_missing_vendor_reference_mass_blocked(self):
        a,b=realistic_fixtures()
        a["TypeII_control_points"].pop("TypeII1000")
        with self.assertRaisesRegex(ValueError,"Missing A1R mass"):
            assess(a,b)

    def test_tanbeta_mismatch_blocks(self):
        a,b=realistic_fixtures()
        b["source_pinned_LO_coefficients"]["300.0"]["tanbeta"]=5.0
        with self.assertRaisesRegex(ValueError,"Yukawa tanbeta"):
            assess(a,b)

    def test_duplicate_modern_zee_shift_change_blocks(self):
        a,b=realistic_fixtures()
        b["selected_Zee_scalar_sector_benchmark"]["linearized_shift_times_1e4"]+=.01
        with self.assertRaisesRegex(ValueError,"mixing does not close"):
            assess(a,b)

    def test_unsupported_zee_masses_block(self):
        a,b=realistic_fixtures()
        b["selected_Zee_scalar_sector_benchmark"]["mH2_GeV"]=670.
        with self.assertRaisesRegex(ValueError,"Zee mass points"):
            assess(a,b)

    def test_nonfinite_legacy_observable_blocks(self):
        a,b=realistic_fixtures()
        a["TypeII_control_points"]["TypeII300"]["BR_B_to_Xs_gamma"]=float("nan")
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            assess(a,b)

if __name__=="__main__":
    unittest.main()
