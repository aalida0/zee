"""Gate A1D neutral-scalar LFV regression tests."""
import pathlib
import sys
import unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1d_neutral_tree_lfv import (
    chen_tableI_NO,tau_tree_br,wilson,scalar_couplings,report
)

class TestNeutralTreeLFV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=report()

    def test_chen_2025_two_published_modes(self):
        for item in self.data["published_benchmark"].values():
            self.assertTrue(item["printed_precision_reproduction_within_5pct"])

    def test_aligned_smh_is_flavour_diagonal(self):
        Y=chen_tableI_NO()
        h,H,A=scalar_couplings(Y,alpha=0,beta=0)
        self.assertAlmostEqual(abs(h[0][2,1]),0,places=18)
        self.assertAlmostEqual(abs(H[0][2,1]),abs(Y[2,1]),places=17)
        self.assertAlmostEqual(abs(A[0][2,1]),abs(Y[2,1]),places=17)

    def test_same_chirality_HA_cancellation(self):
        D=wilson(chen_tableI_NO(),daughter=1,mH=200,mA=200,
                 alpha=0,beta=0)
        self.assertLess(abs(D["RR"]),1e-24)
        self.assertLess(abs(D["LL"]),1e-24)
        self.assertGreater(abs(D["RL"]),1e-10)

    def test_Y_scaling_and_heavy_mass_decoupling(self):
        Y=chen_tableI_NO()
        base,_=tau_tree_br(Y,daughter=1,mH=150,mA=200,alpha=0,beta=0)
        scaledY,_=tau_tree_br(2*Y,daughter=1,mH=150,mA=200,alpha=0,beta=0)
        scaledMass,_=tau_tree_br(Y,daughter=1,mH=300,mA=400,alpha=0,beta=0)
        self.assertAlmostEqual(scaledY/base,16,places=12)
        self.assertAlmostEqual(scaledMass/base,1/16,places=12)

    def test_neutral_h_misalignment_contributes(self):
        Y=np.zeros((3,3),complex)
        Y[2,1]=1e-5
        zero,_=tau_tree_br(Y,daughter=1,alpha=0,beta=0)
        nonzero,_=tau_tree_br(Y,daughter=1,alpha=1.398,beta=1.394)
        self.assertEqual(zero,0)
        self.assertGreater(nonzero,0)

    def test_candidate_only_partial(self):
        r=self.data
        self.assertIn("NOT_FULL",r["status"])
        self.assertAlmostEqual(
            r["candidate_neutral_tree_only"]["tau_to_3mu"]["neutral_tree_only_BR_NOT_total"],
            1.6368895e-23,delta=1e-26)
        self.assertAlmostEqual(
            r["candidate_neutral_tree_only"]["tau_to_e_mumu"]["neutral_tree_only_BR_NOT_total"],
            2.858558e-26,delta=1e-29)

if __name__=="__main__":
    unittest.main()
