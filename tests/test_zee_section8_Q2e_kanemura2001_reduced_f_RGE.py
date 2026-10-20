"""Regression of Kanemura et al (2001) Appendix A *REDUCED REAL f*
RGE. This is NOT a general complex Zee lepton beta calculation.
"""
import math
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_Q2e_kanemura2001_reduced_f_RGE import (
    STATUS,GAUGE_B,LOOP,initial,check_f,f_invariant,
    beta_f_matrix,beta_f_reduced,beta_reduced,run
)

class TestQ2eKanemura2001Reduced(unittest.TestCase):
    def test_source_gauge_coefficients(self):
        self.assertAlmostEqual(GAUGE_B[0],22/3)
        self.assertEqual(GAUGE_B[1:],(-3.,-7.))

    def test_A13_two_independent_implementations_agree(self):
        rng=np.random.default_rng(77)
        for _ in range(25):
            m=rng.normal(size=(3,3))*.1
            f=(m-m.T)/2
            a=beta_f_matrix(f,.36,.65)
            b=beta_f_reduced(f,.36,.65)
            np.testing.assert_allclose(a,b,rtol=1e-12,atol=1e-13)

    def test_A13_cubic_identity_for_real_3D(self):
        rng=np.random.default_rng(123)
        for _ in range(10):
            f=rng.normal(size=(3,3))*.04
            f=f-f.T
            q=f_invariant(f)
            np.testing.assert_allclose(f@f@f,-q*f,rtol=1e-12,atol=1e-14)
            self.assertAlmostEqual(np.sum(f*f),2*q,places=13)

    def test_A13_zero_f_is_fixed(self):
        z=np.zeros((3,3))
        np.testing.assert_array_equal(beta_f_matrix(z,.36,.65),z)
        r=run(steps=12,f=z)
        self.assertEqual(r["q_final"],0.)
        self.assertIsNone(r["f_scale_ratio_sqrt_q"])

    def test_real_orthogonal_flavour_rotation(self):
        rng=np.random.default_rng(22)
        Q=np.linalg.qr(rng.normal(size=(3,3)))[0]
        f=initial()[2]
        rotated=Q@f@Q.T
        lhs=beta_f_matrix(rotated,.36,.65)
        rhs=Q@beta_f_matrix(f,.36,.65)@Q.T
        np.testing.assert_allclose(lhs,rhs,rtol=1e-12,atol=1e-14)

    def test_A12_top_beta_coefficient(self):
        g=np.array([.36,.65,1.18])
        y=.95
        z=np.zeros((3,3))
        dg,dy,df=beta_reduced(g,y,z)
        expected=y*(-17/12*g[0]**2-9/4*g[1]**2-
                     8*g[2]**2+4.5*y*y)
        self.assertAlmostEqual(dy,expected,places=14)
        np.testing.assert_allclose(dg,
            np.array(GAUGE_B)*g**3,rtol=1e-14)
        np.testing.assert_array_equal(df,z)

    def test_real_antisymmetric_restriction_fail_closed(self):
        f=initial()[2]
        for bad in (f.astype(complex),np.zeros((2,3)),
                    np.full((3,3),float("nan"))):
            with self.assertRaises(ValueError):
                check_f(bad)
        m=f.copy()
        m[0,0]=1e-2
        with self.assertRaisesRegex(ValueError,"antisymmetric"):
            beta_f_matrix(m,.36,.65)

    def test_coupled_f_direction_preservation(self):
        result=run(steps=32)
        before=np.array(result["f_initial"])
        after=np.array(result["f_final"])
        scale=result["f_scale_ratio_sqrt_q"]
        np.testing.assert_allclose(after,scale*before,rtol=1e-12,atol=1e-14)
        self.assertLess(result["f_beta_matrix_vs_3d_identity_error"],1e-12)
        self.assertLess(scale,1.)
        self.assertGreater(scale,.9)
        self.assertIsNone(result["physical_Zee_allowed"])

    def test_one_loop_gauge_analytic_running(self):
        initial_couplings=np.array([.36,.65,1.18])
        a=run(steps=60)
        lnmu=math.log(10000/700)
        for idx,(g,b) in enumerate(zip(initial_couplings,GAUGE_B)):
            analytic=(1/g**2-b*lnmu/(8*math.pi**2))**(-.5)
            self.assertAlmostEqual(
                a["gauge_final"][idx],analytic,places=11)

    def test_RK4_steps_60_120_stable(self):
        a=run(steps=60)
        b=run(steps=120)
        self.assertLess(abs(a["f_scale_ratio_sqrt_q"]-
                            b["f_scale_ratio_sqrt_q"]),1e-11)
        self.assertLess(abs(a["top_yukawa_final"]-
                            b["top_yukawa_final"]),1e-10)

    def test_no_full_model_status(self):
        r=run(steps=12)
        self.assertIn("NOT_GENERAL_ZEE_OR_ALLOWED",STATUS)
        for key in ("general_complex_f_supported",
                    "ordinary_lepton_Pi_beta_included",
                    "quartic_lambda6_lambda7_beta_included",
                    "quark_FCNC_likelihood"):
            self.assertFalse(r[key])

if __name__=="__main__":
    unittest.main()
