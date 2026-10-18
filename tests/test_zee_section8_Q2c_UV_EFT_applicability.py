"""Q2c source-gated comprehensive Zee UV/EFT hierarchy + gauge regression.

This does NOT test full renormalizable Zee Yukawa RGEs or experimental
flavor viability. Bibliography: arXiv:2512.17235v2 Eq.(14), Sec.3, App.B.
"""
import math
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_Q2c_UV_EFT_scope_audit import (
    STATUS,V,SOURCE,B_ZEE,B_2HDM,GAUGE_BETA_DERIVATION,
    charged_matrix_audit,run_gauge,gauge_audit,all_cases
)

class TestZeeQ2cSourceApplicability(unittest.TestCase):
    def test_candidate_32_full_mass_matrix_exact_and_reverse_singlet_hierarchy(self):
        r=charged_matrix_audit(208.76954048,681.85192434,1.12012593)
        self.assertAlmostEqual(r["sqrt_M_DD_squared_GeV"],620.472196028,places=6)
        self.assertAlmostEqual(r["sqrt_M_chichi_squared_GeV"],351.455575734,places=6)
        self.assertFalse(r["necessary_heavy_singlet_diagonal_ordering"])
        self.assertTrue(r["light_charged_H1_singlet_dominated"])
        self.assertGreater(r["H1_singlet_weight"],.80)
        self.assertLess(r["broken_phase_mass_matrix_eigenvalue_relative_residual"],1e-12)
        self.assertLess(r["mu_trilinear_identity_relative_residual"],1e-12)
        self.assertIsNone(r["physical_Zee_allowed"])

    def test_candidate_0_full_mass_matrix_exact_and_reverse_singlet_hierarchy(self):
        r=charged_matrix_audit(300.,700.,1.089)
        self.assertAlmostEqual(r["sqrt_M_DD_squared_GeV"],635.7001210668,places=6)
        self.assertAlmostEqual(r["sqrt_M_chichi_squared_GeV"],419.3868811439,places=6)
        self.assertFalse(r["necessary_heavy_singlet_diagonal_ordering"])
        self.assertTrue(r["light_charged_H1_singlet_dominated"])
        self.assertGreater(r["H1_singlet_weight"],.78)
        self.assertAlmostEqual(r["abs_muZee_GeV_from_eq14"],
                               943.400148455,places=5)

    def test_exact_decoupled_singlet_and_doublet_ordering_controls(self):
        # gamma=0: H1 is pure doublet, H2 pure heavy singlet
        a=charged_matrix_audit(300.,1000.,0.)
        self.assertTrue(a["necessary_heavy_singlet_diagonal_ordering"])
        self.assertFalse(a["light_charged_H1_singlet_dominated"])
        self.assertEqual(a["abs_muZee_GeV_from_eq14"],0.)
        # gamma=pi/2: H1 is pure light singlet
        b=charged_matrix_audit(300.,1000.,math.pi/2)
        self.assertFalse(b["necessary_heavy_singlet_diagonal_ordering"])
        self.assertTrue(b["light_charged_H1_singlet_dominated"])
        self.assertAlmostEqual(b["abs_muZee_GeV_from_eq14"],0.,places=10)

    def test_matrix_diagonal_trace_and_det_identity(self):
        for m1,m2,g in ((300.,700.,.3),(250.,650.,1.2),(200.,800.,.85)):
            with self.subTest(g=g):
                r=charged_matrix_audit(m1,m2,g)
                self.assertAlmostEqual(
                    r["M_DD_squared_GeV2"]+r["M_chichi_squared_GeV2"],
                    m1*m1+m2*m2,places=7)
                det=(r["M_DD_squared_GeV2"]*
                     r["M_chichi_squared_GeV2"]-
                     r["M_D_chi_squared_GeV2"]**2)
                self.assertAlmostEqual(det/(m1*m1*m2*m2),1.,places=12)

    def test_z_ee_trilinear_matches_mixing_source_eq14(self):
        for m1,m2,g in ((300.,700.,1.089),(208.76954048,681.85192434,1.12012593)):
            r=charged_matrix_audit(m1,m2,g)
            mu=math.sqrt(2)*abs(r["M_D_chi_squared_GeV2"])/V
            self.assertAlmostEqual(mu,r["abs_muZee_GeV_from_eq14"],places=9)

    def test_gauge_coefficient_singlet_hypercharge(self):
        self.assertEqual(B_2HDM["g1_SM_hypercharge"],7.)
        self.assertAlmostEqual(B_ZEE["g1_SM_hypercharge"],22/3)
        self.assertAlmostEqual(
            B_ZEE["g1_SM_hypercharge"]-B_2HDM["g1_SM_hypercharge"],1/3)
        self.assertEqual(B_ZEE["g2_SU2"],B_2HDM["g2_SU2"])
        self.assertEqual(B_ZEE["g3_SU3"],B_2HDM["g3_SU3"])
        self.assertAlmostEqual(
            GAUGE_BETA_DERIVATION["SM_one_Higgs_doublet_hypercharge_b"]+
            GAUGE_BETA_DERIVATION["extra_SU2_complex_doublet_Y_half"]+
            GAUGE_BETA_DERIVATION["charged_SU2_complex_singlet_Y_one"],
            B_ZEE["g1_SM_hypercharge"])

    def test_gauge_analytic_running_semigroup(self):
        for b,g in ((7.,.36),(-3.,.65),(-7.,1.18),(22/3,.36)):
            with self.subTest(b=b):
                a=run_gauge(g,b,700,1000)
                c=run_gauge(a,b,1000,10000)
                direct=run_gauge(g,b,700,10000)
                self.assertAlmostEqual(c,direct,places=13)

    def test_source_scope_gauge_difference_and_no_flavor_claim(self):
        report=gauge_audit(700.,10000.)
        self.assertGreater(
            report["couplings_at_high"]["g1_SM_hypercharge"][
                "fractional_Zee_minus_2HDM_over_2HDM"],0)
        for c in ("g2_SU2","g3_SU3"):
            self.assertAlmostEqual(
                report["couplings_at_high"][c][
                    "fractional_Zee_minus_2HDM_over_2HDM"],0,places=15)
        self.assertFalse(report["thresholds_or_measured_coupling_inputs"])
        self.assertIn("NO_FULL_UV_RGE_OR_ALLOWED",STATUS)
        self.assertIn("2512.17235v2",SOURCE)

    def test_bad_scalar_inputs_fail_closed(self):
        for vals in ((-1.,700.,1.),(700.,300.,1.),(300.,700.,-1.),
                     (300.,700.,math.nan),(300.,300.,.2)):
            with self.subTest(v=vals):
                with self.assertRaises(ValueError):
                    charged_matrix_audit(*vals)

    def test_bad_gauge_input_fails_closed(self):
        for args in ((.36,7.,-1.,100.),(.36,7.,100.,-1.),
                     (.36,7.,10000.,700.),(0.,7.,700.,1000.),
                     (.36,float("nan"),700.,1000.)):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    run_gauge(*args)

    def test_candidate_mismatch_never_silently_ignored(self):
        p={"id":"32","mH1":208.76954048,"mH2":681.85192434,
           "gamma":1.12012593,"beta":1.395}
        with self.assertRaisesRegex(ValueError,"Mismatched candidate"):
            all_cases({"32":p},{"0":[]},20)
        with self.assertRaisesRegex(ValueError,"exactly 10"):
            all_cases({"32":p},{"32":[]},20)

if __name__=="__main__":
    unittest.main()
