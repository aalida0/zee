"""Regression checks for the limited Chen 2025 Zee neutrino Gate A1."""
import pathlib
import sys
import unittest
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1_chen2025_pilot import (
    PRINTED, HALF_DIGIT, matrices, neutrino_matrix,
    spectrum, rounding_compatible, report, scalar_kappa
)

class GateA1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = report()

    def test_symmetric_mass_antisymmetric_yukawa(self):
        f, Y = matrices(PRINTED)
        M = neutrino_matrix(PRINTED)
        self.assertLess(np.max(abs(f+f.T)), 1e-20)
        self.assertLess(np.max(abs(M-M.T)), 1e-20)

    def test_source_table_mass_scale(self):
        obs = spectrum(neutrino_matrix(PRINTED))
        self.assertAlmostEqual(obs["sum_m_eV"], .220, delta=.004)
        self.assertAlmostEqual(obs["m_bb_eV"], .068, delta=.003)

    def test_rounding_and_individual_oscillation_ranges(self):
        p = rounding_compatible()
        self.assertTrue(np.all(abs(p-PRINTED) < HALF_DIGIT))
        self.assertTrue(self.result["all_five_individual_ranges_pass"])

    def test_scalar_rescaling(self):
        scalar = self.result["scalar_candidate"]
        self.assertTrue(scalar["kinematically_open"])
        self.assertGreater(abs(scalar["sin_2gamma"]), .8)
        self.assertAlmostEqual(abs(scalar_kappa()), .0124633568977, places=10)
        self.assertLess(scalar["matrix_closure_max_abs_eV"], 1e-11)

if __name__ == "__main__":
    unittest.main()
