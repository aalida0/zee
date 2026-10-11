"""Tests for Lavoura neutral-scalar one-loop dipoles and external benchmark."""
import pathlib
import sys
import unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1e_neutral_one_loop_dipoles import (
    loop_A,loop_B,neutral_dipole_for_scalar,
    leading_log_herrero_mu_to_e,total_neutral_dipoles,report
)
from gateA1b_hierarchical_no_seed import ME,MMU,MTAU

class TestNeutralOneLoopDipoles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=report()

    def test_loop_functions_small_t_limits(self):
        self.assertAlmostEqual(loop_A(1e-12),1/6,delta=1e-8)
        self.assertAlmostEqual(loop_B(1e-12),
                               -1.5-np.log(1e-12),delta=1e-8)

    def test_herrero_independent_leading_log(self):
        Y=np.zeros((3,3),complex)
        Y[0,2]=.004-.002j
        Y[2,1]=.03+.01j
        CL,CR=neutral_dipole_for_scalar(Y,400,parent=1,daughter=0)
        LL=leading_log_herrero_mu_to_e(Y,400)
        self.assertLess(abs(abs(CL/LL)-1),1e-4)
        self.assertLess(abs(CR),1e-25)

    def test_flavour_diagonal_has_zero_lfv(self):
        C=np.diag([.001,.01,.02])
        for i,j in [(1,0),(2,1),(2,0)]:
            self.assertEqual(neutral_dipole_for_scalar(
                C,400,parent=i,daughter=j),(0j,0j))

    def test_complex_chirality_and_coherent_sum(self):
        Y=np.zeros((3,3),complex)
        Y[0,2]=.003+.002j
        Y[2,1]=.02+.01j
        CL,CR,_=total_neutral_dipoles(Y,parent=1,daughter=0)
        self.assertTrue(np.isfinite(CL.real))
        self.assertTrue(np.isfinite(CR.real))
        self.assertGreater(abs(CL),0)

    def test_expected_seed_neutral_amplitudes(self):
        for key,ref in (
            ("mu_to_e_gamma",2.0129534244078103e-22),
            ("tau_to_mu_gamma",7.759642253885646e-21),
            ("tau_to_e_gamma",1.0036151078689914e-23),
        ):
            obs=self.data["channels"][key]["neutral_one_loop_only_BR_NOT_total"]
            self.assertAlmostEqual(obs,ref,delta=2e-24*max(1,ref/2e-22))
        self.assertIn("NOT_FULL",self.data["status"])

if __name__=="__main__":
    unittest.main()
