"""A1U: protect physical legacy SuperIso mixed-state BR against false passes."""
from __future__ import annotations
import math
from pathlib import Path
import tempfile
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1u_run_legacy_two_state_br import (
    STATUS,audit_affine_internal_matching,parse_driver,finalize,
)

TAN=5.597170833164245
SM=.0003382457724
R1=.00045115303105
R2=.00037793429732

def fake_raw(m1=300.,m2=700.,g=1.089,b0=.000390,b1=.000393,
             b2=.000391,d1_7=-.10,d2_7=-.05,
             d1_8=-.08,d2_8=-.04, mode="reload"):
    w1=math.cos(g)**2
    w2=math.sin(g)**2
    br=b0+w1*(b1-b0)+w2*(b2-b0) if mode=="reload" else b0
    return (
        "STATUS "+STATUS+"\n"
        f"INTERNAL_CW_MODE={mode}\n"
        f"INPUT mH1_GeV={m1:.17g} mH2_GeV={m2:.17g} "
        f"gamma_rad={g:.17g} tanbeta={TAN:.17g} "
        "muW_GeV=160.7384 mu_b_GeV=2.4\n"
        f"WEIGHTS w1={w1:.17g} w2={w2:.17g}\n"
        f"MATCH op=7 sm_LO=-0.20000000000000001 "
        f"delta1_LO={d1_7:.17g} delta2_LO={d2_7:.17g} "
        f"zee_LO={-.2+w1*d1_7+w2*d2_7:.17g}\n"
        f"MATCH op=8 sm_LO=-0.10000000000000001 "
        f"delta1_LO={d1_8:.17g} delta2_LO={d2_8:.17g} "
        f"zee_LO={-.1+w1*d1_8+w2*d2_8:.17g}\n"
        f"A1U_CONTEXT_DIAGNOSTIC RG_MAX_ABS_DELTA_H1=0 "
        f"RG_MAX_ABS_DELTA_H2=0 "
        f"FIXED_LOW_BR_SM={b0:.17g} "
        f"FIXED_LOW_BR_H1={b1:.17g} FIXED_LOW_BR_H2={b2:.17g}\n"
        f"INTERNAL_FIXED_LOW BR_SM_CONTEXT={b0:.17g} "
        f"BR_H1_CONTEXT={b1:.17g} BR_H2_CONTEXT={b2:.17g}\n"
        f"FULL_SINGLE_REFERENCE br_H1={R1:.17g} "
        f"br_H2={R2:.17g} br_SM={SM:.17g}\n"
        f"FULL_LEGACY_ZEE_TWO_STATE_BR={br:.17g}\n"
        "EXPERIMENTAL_LIKELIHOOD_VALIDATED false\n"
        "MODERN_2026_FULL_NNLO_VALIDATED false\n"
        "ZEE_BENCHMARK_ALLOWED_OR_EXCLUDED undetermined\n"
    )

def legacy():
    return {
        "status":"GATE_A1R_SINGLE_TYPEII_OBSERVABLE_BR_PILOT_"
                 "AWAITING_INDEPENDENT_ERROR_BUDGET",
        "SM_model_BR":SM,
        "TypeII_control_points":{
            "TypeII300":{"BR_B_to_Xs_gamma":R1},
            "TypeII700":{"BR_B_to_Xs_gamma":R2},
        }
    }

def cases():
    p=parse_driver(fake_raw(),300.,700.,1.089,TAN)
    zero=parse_driver(fake_raw(g=0.,b1=R1),300.,700.,0.,TAN)
    right=parse_driver(fake_raw(g=math.pi/2,b2=R2),
                       300.,700.,math.pi/2,TAN)
    deg=parse_driver(fake_raw(m1=700.,m2=700.,b1=R2,b2=R2,
                              d1_7=-.05,d1_8=-.04),700.,700.,1.089,TAN)
    return p,zero,right,deg

SOURCE_SAMPLE=(
    "double bsgamma(double complex C0[],double complex C1[],"
    " double complex C2[],double complex Cp[],double mu,double muW,"
    " struct parameters* param) {"
    " double complex Cem[9],C0w[11],C1w[11],C2w[11];"
    " CW_calculator(2,C0w,C1w,C2w,muW,param);"
    " double Kt0=C0w[7] +2*C0w[8];"
    " double N_E0=0.001*Kt0;"
    " Cem[7]=C0w[7]+C0w[8];"
    " return N_E0+Cem[7];"
    " }\n"
    "double bsgamma_calculator(char* file) {return 0.;}\n"
)

class TestGateA1ULegacyTwoState(unittest.TestCase):
    def test_source_contract_recognizes_affine_internal_reload(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"src"
            p.mkdir()
            (p/"bsgamma.c").write_text(SOURCE_SAMPLE)
            report=audit_affine_internal_matching(t)
            self.assertEqual(report["internal_CW_call_count"],1)
            self.assertEqual(report["reloaded_indices"],["7","8"])
            self.assertFalse(report["two_state_modern_2026_BR_validated"])

    def test_v5_helper_reloading_is_detected(self):
        source=(
            "double bsgamma_Ecut(double complex C0[],double complex C1[],"
            "double complex C2[],double complex Cp[],double mu,"
            "double mu_W,double E0,struct parameters* param)"
            "{double complex C0w[11],C1w[11],C2w[11];"
            "CW_calculator(2,C0w,C1w,C2w,mu_W,param);"
            "double Kt0=creal(C0w[7]);"
            "double Cem=creal(C0w[8]); return Kt0+Cem;}\n"
            "double bsgamma(double complex C0[],double complex C1[],"
            "double complex C2[],double complex Cp[],double mu,"
            "double muW,struct parameters* param)"
            "{return bsgamma_Ecut(C0,C1,C2,Cp,mu,muW,1.6,param);}\n"
            "double bsgamma_calculator(char* file){return 0.;}\n"
        )
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"src";p.mkdir()
            (p/"bsgamma.c").write_text(source)
            report=audit_affine_internal_matching(t)
            self.assertEqual(report["internal_CW_mode"],"helper_reload")
            self.assertEqual(report["internal_CW_call_count"],1)
            self.assertEqual(report["reloaded_indices"],[7,8])

    def test_v5_helper_unknown_matching_argument_blocks(self):
        source=(
            "double bsgamma_Ecut(double C0[],double C1[],double C2[],"
            "double Cp[],double mu,double mu_W,double E0,struct parameters* param)"
            "{double C0w[11],C1w[11],C2w[11];"
            "CW_calculator(1,C0w,C1w,C2w,mu_W,param);"
            "return C0w[7]+C0w[8];}\n"
            "double bsgamma(double C0[],double C1[],double C2[],"
            "double Cp[],double mu,double muW,struct parameters* param)"
            "{return bsgamma_Ecut(C0,C1,C2,Cp,mu,muW,1.6,param);}\n"
            "double bsgamma_calculator(char* file){return 0.;}\n"
        )
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"src";p.mkdir()
            (p/"bsgamma.c").write_text(source)
            with self.assertRaisesRegex(ValueError,"signature"):
                audit_affine_internal_matching(t)

    def test_helper_mode_rejects_branching_ratio_interpolation(self):
        raw=fake_raw(mode="none",b1=.000390,b2=.000390)
        raw=raw.replace("INTERNAL_CW_MODE=none",
                        "INTERNAL_CW_MODE=helper_reload")
        result=parse_driver(raw,300.,700.,1.089,TAN,
                            expected_mode="helper_reload")
        self.assertEqual(result["full_legacy_Zee_BR"],.000390)
        with self.assertRaisesRegex(ValueError,"context"):
            parse_driver(fake_raw(mode="reload").replace(
                "INTERNAL_CW_MODE=reload",
                "INTERNAL_CW_MODE=helper_reload"),300.,700.,1.089,TAN)

    def test_source_nonlinear_internal_reload_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"src"
            p.mkdir()
            (p/"bsgamma.c").write_text(SOURCE_SAMPLE.replace(
                "double Kt0=C0w[7] +2*C0w[8]",
                "double Kt0=pow(C0w[7],2)"))
            with self.assertRaisesRegex(ValueError,"Nonlinear"):
                audit_affine_internal_matching(t)

    def test_source_direct_mass_access_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"src"
            p.mkdir()
            (p/"bsgamma.c").write_text(SOURCE_SAMPLE.replace(
                "return N_E0+Cem[7];","return N_E0+Cem[7]+param->mass_H;"))
            with self.assertRaisesRegex(ValueError,"mass/SM"):
                audit_affine_internal_matching(t)

    def test_real_v5_no_reload_source_mode_is_accepted_safely(self):
        source=(
            "double bsgamma(double complex C0[],double complex C1[],"
            " double complex C2[],double complex Cp[], double mu,"
            " double muW,struct parameters* param) {"
            " double Kt0=C0[7] +2*C0[8];"
            " double Cem[9]; Cem[7]=C0[7]+C0[8];"
            " return Kt0+Cem[7];"
            " }\n"
            "double bsgamma_calculator(char* name) {"
            " CW_calculator(2,a,b,c,muW,param); return 0.;}\n"
        )
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"src"
            p.mkdir()
            (p/"bsgamma.c").write_text(source)
            report=audit_affine_internal_matching(t)
            self.assertEqual(report["internal_CW_mode"],"none")
            self.assertEqual(report["internal_CW_call_count"],0)
            self.assertFalse(report["affine_interpolation_needed"])
            self.assertTrue(report["numerical_fixed_low_context_test_required"])
        parsed=parse_driver(fake_raw(b1=.000390,b2=.000390,mode="none"),
                            300.,700.,1.089,TAN,expected_mode="none")
        self.assertTrue(parsed["fixed_low_context_invariance_verified"])
        self.assertAlmostEqual(parsed["full_legacy_Zee_BR"],.000390)

    def test_no_reload_context_mismatch_is_hard_failure(self):
        with self.assertRaisesRegex(ValueError,"context"):
            parse_driver(fake_raw(mode="none"),300.,700.,1.089,TAN)
        with self.assertRaisesRegex(ValueError,"mode differs"):
            parse_driver(fake_raw(mode="reload"),300.,700.,1.089,TAN,
                         expected_mode="none")

    def test_no_reload_source_unknown_high_scale_reference_is_blocked(self):
        source=(
            "double bsgamma(double C0[],double C1[],double C2[],"
            " double Cp[],double mu,double muW,struct parameters* param)"
            " { double C0w[11]; return C0w[7]+C0[7];}\n"
            "double bsgamma_calculator(char* filename) {return 0.;}\n"
        )
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"src"
            p.mkdir()
            (p/"bsgamma.c").write_text(source)
            with self.assertRaisesRegex(ValueError,"without CW reload"):
                audit_affine_internal_matching(t)

    def test_strict_parse_and_affine_internal_math(self):
        p=parse_driver(fake_raw(),300.,700.,1.089,TAN)
        self.assertTrue(0.<p["w_light"]<1.)
        self.assertAlmostEqual(p["w_light"]+p["w_heavy"],1.)
        self.assertTrue(p["full_legacy_Zee_BR"]>0.)
        self.assertTrue(p["C7_C8_high_scale"][7]["delta_light"]<0.)

    def test_corrupted_mixing_math_blocks(self):
        content=fake_raw()
        # A different high-scale C7 or BR would invalidate closure.
        bad=content.replace("zee_LO=-0.260", "zee_LO=-0.261")
        if bad!=content:
            with self.assertRaisesRegex(ValueError,"Wilson mixing closure"):
                parse_driver(bad,300.,700.,1.089,TAN)
        bad=content.replace("FULL_LEGACY_ZEE_TWO_STATE_BR=",
                            "FULL_LEGACY_ZEE_TWO_STATE_BR=0.0001\n"
                            "FULL_LEGACY_ZEE_TWO_STATE_BR=")
        with self.assertRaisesRegex(ValueError,"Missing/duplicate"):
            parse_driver(bad,300.,700.,1.089,TAN)

    def test_endpoint_and_equal_mass_closure_against_real_A1R(self):
        p,l,r,d=cases()
        report=finalize(p,l,r,d,legacy(),{},{},"output.log")
        self.assertTrue(report["all_A1R_physical_endpoint_checks_pass"])
        self.assertTrue(report["full_legacy_two_state_BR_calculated"])
        self.assertFalse(report["MODERN_2026_full_NNLO_two_state_BR_validated"])
        self.assertIsNone(report["Zee_model_allowed"])
        self.assertIsNone(report["Zee_model_excluded"])

    def test_endpoint_reference_shift_blocks_exclusion(self):
        p,l,r,d=cases()
        obj=legacy()
        obj["TypeII_control_points"]["TypeII700"]["BR_B_to_Xs_gamma"]+=1e-5
        with self.assertRaisesRegex(ValueError,"closure failure"):
            finalize(p,l,r,d,obj,{},{},"output.log")

    def test_rg_context_stage_failure_is_not_misclassified_as_bsgamma(self):
        # If the same high-scale Wilson vector evolves differently under
        # H1/H2 contexts, we cannot claim that the problem arises inside
        # bsgamma(); physical single-state checks have not yet run.
        raw=fake_raw().replace(
            "RG_MAX_ABS_DELTA_H1=0",
            "RG_MAX_ABS_DELTA_H1=0.001")
        with self.assertRaisesRegex(ValueError,"RG context invariance"):
            parse_driver(raw,300.,700.,1.089,TAN)

    def test_bsgamma_diagnostic_disagreement_not_silenced(self):
        raw=fake_raw().replace(
            "FIXED_LOW_BR_H2=0.00039100000000000002",
            "FIXED_LOW_BR_H2=0.00040000000000000002")
        self.assertNotEqual(raw,fake_raw())
        with self.assertRaisesRegex(ValueError,
                                    "fixed-low diagnostics disagree"):
            parse_driver(raw,300.,700.,1.089,TAN)

    def test_missing_stage_is_not_accepted(self):
        raw=fake_raw()
        raw="\n".join(line for line in raw.splitlines()
                      if not line.startswith("A1U_CONTEXT_DIAGNOSTIC "))
        with self.assertRaisesRegex(ValueError,"Missing/duplicate A1U field"):
            parse_driver(raw,300.,700.,1.089,TAN)

    def test_malformed_missing_marker_does_not_fake_BR(self):
        raw=fake_raw().replace(
            "MODERN_2026_FULL_NNLO_VALIDATED false","")
        with self.assertRaisesRegex(ValueError,"safety marker"):
            parse_driver(raw,300.,700.,1.089,TAN)

if __name__=="__main__":
    unittest.main()
