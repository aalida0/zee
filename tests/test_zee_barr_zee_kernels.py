"""Barr-Zee loop FUNCTION mathematical validation (no LFV-exclusion claim)."""
from __future__ import annotations
import math
import pathlib
import sys
import unittest
from scipy.integrate import quad

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from zee_barr_zee_kernels import (
    STATUS,_log_over_t,g,f,kernels_for_masses
)


class TestBarrZeeKernels(unittest.TestCase):
    def test_Haber_exact_z_quarter_g_and_f(self):
        gv,err=g(.25)
        fv,_=f(.25)
        self.assertAlmostEqual(gv,math.log(2),delta=1e-9)
        self.assertAlmostEqual(fv,.5,delta=1e-9)
        self.assertLess(err,1e-8)

    def test_Haber_z_one_g_and_f(self):
        gv,_=g(1.)
        fv,_=f(1.)
        self.assertAlmostEqual(gv,1.1719536193447295,delta=2e-9)
        self.assertAlmostEqual(fv,.8280463806552705,delta=2e-9)
        self.assertAlmostEqual(gv+fv,2,delta=1e-10)

    def test_independent_direct_quadrature_formula(self):
        # Completely different integrand, directly from Haber Eq. (1);
        # check at representative top/H ratio and above-threshold value.
        for z in (.08, .4, 2.):
            def raw_integrand(x):
                u=x*(1-x)
                if abs(u-z)<1e-10:
                    return z*.5/z
                return .5*z*math.log(u/z)/(u-z)
            expected,_=quad(raw_integrand,0,1,epsabs=2e-10,limit=300)
            got,_=g(z)
            self.assertAlmostEqual(got,expected,delta=5e-9)

    def test_exact_f_g_identity(self):
        for z in (0.0001,.08,.25,1.,2.,10.):
            gg,_=g(z)
            ff,_=f(z)
            expected=z*(2+math.log(z))+(1-2*z)*gg
            self.assertAlmostEqual(ff,expected,delta=1e-12)

    def test_near_removable_singularity(self):
        self.assertEqual(_log_over_t(0.),1.)
        self.assertAlmostEqual(_log_over_t(1e-9),1.-.5e-9,
                               delta=1e-15)
        self.assertAlmostEqual(_log_over_t(-1e-9),1.+.5e-9,
                               delta=1e-15)

    def test_invalid_inputs_fail_closed(self):
        for z in (0.,-1.,float("nan"),float("inf"),1e-15):
            with self.assertRaises(ValueError):
                g(z)
        with self.assertRaises(ValueError):
            kernels_for_masses({"H":-500})

    def test_realistic_top_bottom_tau_loop_evaluation(self):
        rows=kernels_for_masses({"h125":125.,"H":600.,"A":635.})
        self.assertEqual(len(rows),9)
        self.assertTrue(all(r["f_scalar"]>0 and
                            r["g_pseudoscalar"]>0 for r in rows))
        self.assertTrue(all("NO_DIPOLERATE_OR_EXCLUSION" in r["status"]
                            for r in rows))
        self.assertIn("NOT_LFV_EXCLUSION",STATUS)

if __name__=="__main__":
    unittest.main()
