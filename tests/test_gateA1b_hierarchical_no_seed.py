"""Gate A1B regression tests: generalized Zee neutrino seed algebra."""
import pathlib
import sys
import unittest
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix, antisymmetric_f_with_null_condition,
    solve_lepton_yukawa, reconstruct_neutrino, pmns, report
)

class TestGeneralZeeSeed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = report()

    def test_pmns_unitary_and_target_symmetric(self):
        U = pmns()
        M, _ = target_neutrino_matrix()
        self.assertLess(np.max(abs(U.conj().T@U-np.eye(3))), 1e-12)
        self.assertLess(np.max(abs(M-M.T)), 1e-12)

    def test_exact_antisymmetric_and_null_cone(self):
        M, _ = target_neutrino_matrix()
        f, n = antisymmetric_f_with_null_condition(M)
        self.assertLess(np.max(abs(f+f.T)), 1e-15)
        self.assertLess(np.max(abs(f@n)), 1e-15)
        self.assertLess(abs(n.T@M@n), 1e-12)

    def test_rank_five_and_complex_matrix_closure(self):
        M, _ = target_neutrino_matrix()
        f, _ = antisymmetric_f_with_null_condition(M)
        Y, rank, _ = solve_lepton_yukawa(f, M)
        self.assertEqual(rank, 5)
        self.assertLess(np.max(abs(reconstruct_neutrino(f,Y)-M)), 1e-10)
        self.assertLess(np.max(abs(f)), .001000000001)
        self.assertLess(np.max(abs(Y)), 1e-3)

    def test_hierarchical_sum_and_takagi(self):
        r = self.result
        self.assertLess(r["sum_m_eV"], .0642)
        self.assertGreater(r["sum_m_eV"], .059)
        self.assertLess(r["max_takagi_diagonal_closure_abs_eV"], 1e-10)
        self.assertTrue(r["scalar_inputs"]["cascade_kinematically_open"])

if __name__ == "__main__":
    unittest.main()
