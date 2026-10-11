"""Analytic mixed-pair production regression tests.

Run under Key4hep: python3 -m unittest discover -s tests -v
No real PDF set needed for these unit tests.
"""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from fcc_hh_mixed_pair_dy import (
    GEV2_TO_FB, lambda_kallen, rate_pp_mixed_pair,
    sigmahat_qqbar_to_h1h2, zee_g12, g12_scaled_to_gamma, G12_P2_PILOT
)


class UnitPDF:
    """Artificial f_q(x)=f_antiq(x)=1 => xfxQ=x."""
    def xfxQ(self,pid,x,Q):
        assert 0<x<1 and Q>0
        return x


class MixedPairTest(unittest.TestCase):
    def test_threshold(self):
        self.assertEqual(sigmahat_qqbar_to_h1h2(1000**2,300,700,2),0)
        self.assertEqual(lambda_kallen(1000**2,300,700),0)

    def test_legacy_benchmark_g12_unchanged(self):
        self.assertAlmostEqual(g12_scaled_to_gamma(1.089), G12_P2_PILOT, places=13)

    def test_gamma_scan_scaling(self):
        a = g12_scaled_to_gamma(.4)
        b = g12_scaled_to_gamma(.8)
        self.assertAlmostEqual(a/b, math.sin(.8)/math.sin(1.6), places=12)
        self.assertEqual(g12_scaled_to_gamma(0), 0)

    def test_mixing_zero(self):
        self.assertEqual(zee_g12(0),0)
        self.assertEqual(sigmahat_qqbar_to_h1h2(2000**2,300,700,2,g12=0),0)

    def test_mass_exchange_symmetry(self):
        a=sigmahat_qqbar_to_h1h2(2000**2,300,700,2)
        b=sigmahat_qqbar_to_h1h2(2000**2,700,300,2)
        self.assertAlmostEqual(a,b)

    def test_scalar_pair_qed_limit(self):
        # For e+e−→ charged scalars via photon (n_color=1):
        # sigmahat = pi*alpha^2/(3*s) in the massless-scalar limit.
        alpha=1/137.036
        e2=4*math.pi*alpha
        s=2000**2
        direct=(e2*e2)*2*s**3/(96*math.pi*s**4)
        reference=math.pi*alpha**2/(3*s)
        self.assertAlmostEqual(direct,reference,places=23)

    def test_pdf_convolution_against_independent_tau_integral(self):
        from scipy.integrate import quad
        e_tev=5.
        ss=(1000*e_tev)**2
        t0=1000**2/ss
        # UnitPDF -> per-flavor luminosity = 2 ln(1/tau);
        # two charge assignments => factor of 4.
        expected=quad(
            lambda tau:4*math.log(1/tau)*
               sigmahat_qqbar_to_h1h2(tau*ss,300,700,2)*GEV2_TO_FB,
            t0,1.,epsrel=1e-8)[0]
        result=rate_pp_mixed_pair(
            UnitPDF(),sqrt_s_tev=e_tev,flavors=(2,),
            nodes_tau=60,nodes_y=24)
        self.assertAlmostEqual(result["sigma_both_charges_fb"]/expected,
                               1.,delta=.001)
        self.assertAlmostEqual(
            result["sigma_both_charges_fb"]/result["sigma_per_charge_fb"],
            2.)

    def test_quadrature_stability(self):
        a=rate_pp_mixed_pair(UnitPDF(),sqrt_s_tev=5.,
            flavors=(1,2),nodes_tau=36,nodes_y=12)
        b=rate_pp_mixed_pair(UnitPDF(),sqrt_s_tev=5.,
            flavors=(1,2),nodes_tau=72,nodes_y=30)
        self.assertAlmostEqual(
            a["sigma_both_charges_fb"]/b["sigma_both_charges_fb"],
            1.,delta=.005)


if __name__=="__main__":
    unittest.main()
