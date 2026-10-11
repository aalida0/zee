"""Tests for the restricted charged-singlet f-only LFV contribution."""
import pathlib
import sys
import unittest
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1c_charged_singlet_lfv import (
    singlet_propagator_sum, dipole_coefficient_f_only,
    branching_fraction_f_only, report, CHANNELS,
)
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix, antisymmetric_f_with_null_condition, GAMMA, M1, M2
)

class ChargedSingletLFV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = report()
        cls.f, _ = antisymmetric_f_with_null_condition(target_neutrino_matrix()[0])

    def test_singlet_weights_and_zero_mixing_limits(self):
        self.assertAlmostEqual(singlet_propagator_sum(0., M1, M2), 1/M2**2, places=17)
        self.assertAlmostEqual(singlet_propagator_sum(np.pi/2, M1, M2), 1/M1**2, places=17)

    def test_conjugate_row_product_flavour_order(self):
        i,j = 1,0
        C = dipole_coefficient_f_only(self.f,i,j)
        explicit = -sum(np.conj(self.f[j,k])*self.f[i,k]
                        for k in range(3))*singlet_propagator_sum()/(48*np.pi**2)
        self.assertAlmostEqual(abs(C-explicit), 0., places=27)
        self.assertEqual(dipole_coefficient_f_only(np.zeros((3,3),complex),i,j),0)

    def test_scaling_and_degenerate_mass_limit(self):
        B = branching_fraction_f_only(self.f, 1, 0, 1.)
        B2 = branching_fraction_f_only(self.f*2, 1, 0, 1.)
        self.assertAlmostEqual(B2/B, 16)
        # For degenerate charged masses, mixing angle cancels by unitarity.
        a = singlet_propagator_sum(0.21, 400, 400)
        b = singlet_propagator_sum(1.27, 400, 400)
        self.assertAlmostEqual(a,b,places=17)

    def test_expected_f_only_scale_and_not_a_full_lfv_pass(self):
        channel = self.data["channels"]["mu_to_e_gamma"]
        self.assertAlmostEqual(channel["f_only_noninterfering_BR"],1.55740710952e-18,delta=1e-23)
        self.assertLess(channel["f_only_over_exp_limit"],1e-4)
        self.assertIn("NOT_FULL",self.data["status"])
        self.assertGreater(len(self.data["not_checked"]),4)

if __name__ == "__main__":
    unittest.main()
