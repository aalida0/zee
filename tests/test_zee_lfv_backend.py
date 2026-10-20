"""B5 regression: new 3lepton neutral trees and general f universality.

B5 is NOT a complete Zee LFV likelihood. Test exact published A1D
overlap and Yukawa-convention identities before using its diagnostics.
"""
from __future__ import annotations
import math
import pathlib
import sys
import unittest
import numpy as np

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1d_neutral_tree_lfv import chen_tableI_NO,tau_tree_br
from gateB3_general_zee_charged_lepton_widths import read_b1
from zee_lfv_backend import (
    STATUS,TREE_CHANNELS,general_neutral_tree_coefficients,
    general_neutral_tree_BR,f_only_universality,
)

class TestZeeExtendedPartialLFV(unittest.TestCase):
    def test_status_must_not_claim_complete_lfv(self):
        self.assertIn("NOT_ALLOWED",STATUS)
        self.assertIn("PARTIAL",STATUS)
        self.assertIn("mu_to_3e_tree",TREE_CHANNELS)

    def test_reproduce_preexisting_tau3mu_exactly(self):
        Y=chen_tableI_NO()
        new,D=general_neutral_tree_BR(
            Y,parent=2,daughter=1,spectator=1,norm_br=.1739,
            mh=125,mH=150,ma=200,alpha=0,beta=0)
        old,Dold=tau_tree_br(
            Y,daughter=1,mh=125,mH=150,mA=200,alpha=0,beta=0)
        self.assertAlmostEqual(new,old,delta=max(1e-35,old*1e-12))
        for k in D:
            self.assertAlmostEqual(abs(D[k]-Dold[k]),0,delta=1e-19)

    def test_reproduce_preexisting_tau_e_mumu_exactly(self):
        Y=chen_tableI_NO()
        new,_=general_neutral_tree_BR(
            Y,parent=2,daughter=0,spectator=1,norm_br=.1782,
            mH=150,ma=200,alpha=0,beta=0)
        old,_=tau_tree_br(
            Y,daughter=0,mH=150,mA=200,alpha=0,beta=0)
        self.assertAlmostEqual(new,old,delta=max(1e-35,old*1e-12))

    def test_diagonal_y_has_zero_neutral_tree_flavor(self):
        Y=np.diag([1.e-3,2.e-2,.03]).astype(complex)
        for parent,daughter,spectator,norm,_ in TREE_CHANNELS.values():
            br,_=general_neutral_tree_BR(
                Y,parent=parent,daughter=daughter,spectator=spectator,
                norm_br=norm,mH=500,ma=600,alpha=0,beta=0)
            self.assertEqual(br,0.)

    def test_mu_to_3e_scales_like_y_to_fourth(self):
        Y=np.zeros((3,3),complex)
        Y[0,1]=1e-4+2e-4j
        Y[0,0]=2e-3
        kw=dict(parent=1,daughter=0,spectator=0,norm_br=1,
                mH=450,ma=550,alpha=0,beta=0)
        one,_=general_neutral_tree_BR(Y,**kw)
        two,_=general_neutral_tree_BR(2*Y,**kw)
        self.assertGreater(one,0)
        self.assertAlmostEqual(two/one,16,delta=1e-11)

    def test_H_A_same_chirality_cancellation(self):
        Y=np.zeros((3,3),complex)
        Y[0,1]=1e-4
        Y[0,0]=.01
        D=general_neutral_tree_coefficients(
            Y,parent=1,daughter=0,spectator=0,
            mH=500,ma=500,alpha=0,beta=0)
        self.assertLess(abs(D["LL"]),1e-23)
        self.assertLess(abs(D["RR"]),1e-23)
        self.assertGreater(abs(D["LR"]),1e-12)

    def test_f_only_universality_zero_and_general_nonzero_f_e_mu(self):
        f=np.zeros((3,3),complex)
        res=f_only_universality(f,300,700,1.)
        self.assertTrue(all(v==0 for v in res.values()))
        f[0,1]=.002;f[1,0]=-.002
        r=f_only_universality(f,300,700,1.)
        self.assertGreater(r["GF_mu_over_GF_SM_squared_minus1_f_only"],0)
        self.assertAlmostEqual(
            r["g_tau_over_mu_squared_minus1_f_only"],
            -r["GF_mu_over_GF_SM_squared_minus1_f_only"],places=15)
        self.assertAlmostEqual(
            r["g_tau_over_e_squared_minus1_f_only"],
            -r["GF_mu_over_GF_SM_squared_minus1_f_only"],places=15)
        self.assertAlmostEqual(
            r["g_mu_over_e_squared_minus1_f_only"],0.,places=15)

    def test_f_only_universality_recovers_2017_f_e_mu_zero_limit(self):
        f=np.zeros((3,3),complex)
        f[0,2]=.0005;f[2,0]=-.0005
        f[1,2]=.0008;f[2,1]=-.0008
        r=f_only_universality(f,300,700,.9)
        self.assertEqual(r["GF_mu_over_GF_SM_squared_minus1_f_only"],0.)
        self.assertGreater(
            r["g_tau_over_mu_squared_minus1_f_only"],0)
        self.assertGreater(
            r["g_tau_over_e_squared_minus1_f_only"],
            r["g_tau_over_mu_squared_minus1_f_only"])
        self.assertAlmostEqual(
            r["g_mu_over_e_squared_minus1_f_only"],
            r["g_tau_over_e_squared_minus1_f_only"]-
            r["g_tau_over_mu_squared_minus1_f_only"],places=16)

    def test_antisymmetry_checked(self):
        f=np.eye(3,dtype=complex)
        with self.assertRaisesRegex(ValueError,"antisymmetric"):
            f_only_universality(f,300,700,1.)

    def test_invalid_flavor_indices_rejected(self):
        Y=np.zeros((3,3),complex)
        with self.assertRaisesRegex(ValueError,"Invalid flavor"):
            general_neutral_tree_BR(
                Y,parent=1,daughter=1,spectator=0,norm_br=1,
                mH=500,ma=600,alpha=0,beta=0)


if __name__=="__main__":
    unittest.main()
