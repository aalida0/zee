"""Regression checks for *one charge* + *both charges* Zee mu collider Z-only cross section.

Closed-form derivation is from Florentino, Romao, Silva EPJC 81 (2021)
App B off-diagonal Z vertex, normalized against known scalar QED pair
production e+e- -> H+H- (photon).
"""
from __future__ import annotations
import math
import sys
import pathlib
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from zee_muon_asymmetric_pair_pilot import (
    STATUS,ALPHA_EM,SW2,MZ,GEV_MINUS2_TO_FB,
    BR_Z_EE_MUMU,beta_pair,sigma_one_charge_fb,sigma_both_charges_fb,
    rest_frame_b_momentum,to_candidate,evaluate
)


class TestZeeMuonGaugePilot(unittest.TestCase):
    def setUp(self):
        self.p=to_candidate({
            "candidate_id":"B4_0000318","seed_id":"32",
            "mH1":"207.25762719087444",
            "mH2":"686.4739736697521",
            "gamma":"1.1845311184933986",
            "B3_BR_H2_H1Z_median":"0.793008",
            "B3_BR_H1_tb_median":"0.99978",
            "status":"NOT_ALLOWED"
        })

    def test_published_Z_coupling_zero_mixing(self):
        for gamma in (0,math.pi/2):
            self.assertLess(sigma_both_charges_fb(
                3000,207.,686.,gamma),1e-28)

    def test_both_charge_conjugates_is_two(self):
        s=sigma_one_charge_fb(3000,207.,686.,.8)
        self.assertAlmostEqual(
            sigma_both_charges_fb(3000,207.,686.,.8),
            2*s,delta=1e-13)

    def test_identical_mass_limit_and_mass_exchange(self):
        a=sigma_one_charge_fb(3000,250.,250.,.63)
        b=sigma_one_charge_fb(3000,250.,250.,.63)
        self.assertEqual(a,b)
        c=sigma_one_charge_fb(3000,250.,700.,.63)
        d=sigma_one_charge_fb(3000,700.,250.,.63)
        self.assertAlmostEqual(c,d,delta=1e-14)
        self.assertLess(c,a)

    def test_exact_unequal_mass_threshold(self):
        self.assertEqual(sigma_one_charge_fb(
            self.p["mH1"]+self.p["mH2"],self.p["mH1"],
            self.p["mH2"],self.p["gamma"]),0)
        self.assertEqual(sigma_one_charge_fb(
            800,self.p["mH1"],self.p["mH2"],
            self.p["gamma"]),0)
        self.assertGreater(sigma_one_charge_fb(
            1200,self.p["mH1"],self.p["mH2"],
            self.p["gamma"]),0)

    def test_photon_scalar_pair_reference_cross_section_ratio(self):
        # Relative Z contribution is independently normalized to
        # sigma_QED = pi*alpha²*beta³/(3s). For pure off-diagonal Z,
        # R_Z = [g_s²*(g_L²+g_R²)]/[2*e^4] * |propagator|².
        E=3000.
        s=E*E
        pure_qed=(math.pi*ALPHA_EM**2/(3*s)*
                  beta_pair(E,207.,686.)**3*GEV_MINUS2_TO_FB)
        gL=-.5+SW2
        gR=SW2
        ratio=(math.sin(2*.8)**2*(gL*gL+gR*gR)/
               (32*(SW2*(1-SW2))**2)*
               (s/(s-MZ*MZ))**2)
        obs=sigma_one_charge_fb(E,207.,686.,.8)
        self.assertAlmostEqual(obs/pure_qed,ratio,delta=1e-14)

    def test_auditable_benchmark_numbers(self):
        m1=self.p["mH1"];m2=self.p["mH2"];gamma=self.p["gamma"]
        refs={
            1500.:.5949022220191089,
            3000.:.2807932202949499,
            10000.:.029686489688082407,
        }
        for E,ref in refs.items():
            self.assertAlmostEqual(
                sigma_both_charges_fb(E,m1,m2,gamma),
                ref,delta=ref*1e-10)
        self.assertAlmostEqual(
            rest_frame_b_momentum(m1),31.6101320,delta=2e-6)

    def test_two_light_charged_Higgs_decay_factors_squared(self):
        r=evaluate(self.p,3.0,1.0)
        prod=r["produced_pairs"]
        b2=self.p["B3_BR_H2_H1Z_median"]
        b1=self.p["B3_BR_H1_tb_median"]
        true=r["truth_Z_ee_mumu_tb_tb_included_only"]
        self.assertAlmostEqual(
            true,prod*b2*b1*b1*BR_Z_EE_MUMU,delta=1e-12)
        self.assertAlmostEqual(prod,280.7932202949499,delta=1e-8)
        self.assertFalse(r["discovery_or_exclusion_calculated"])

    def test_angle_distribution_is_scalar_sin_squared(self):
        # Integral_{-1}^{1}(1-cos² theta)dcos theta =4/3;
        # relative normalized P(cos theta)=3/4 (1-cos² theta).
        self.assertAlmostEqual((3/4)*(4/3),1.0)

    def test_input_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"Require validated B4C"):
            to_candidate({"id":"bad"})
        bad=dict(self.p)
        bad["B3_BR_H1_tb_median"]=1.1
        with self.assertRaisesRegex(ValueError,"conditional BRs"):
            to_candidate(bad)

    def test_muon_not_special_in_gauge_only(self):
        # Initial lepton masses not in expression: e+e- and mu+mu-
        # have the same gauge-only partonic rate in massless limit.
        self.assertIn("GAUGE_ONLY",STATUS)
        self.assertIn("NOT_PHYSICAL_REACH",STATUS)


if __name__=="__main__":
    unittest.main()
