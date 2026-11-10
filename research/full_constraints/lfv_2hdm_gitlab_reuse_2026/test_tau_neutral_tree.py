import math
import unittest

from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_neutral_tree import (
    CARD_IDS, GAMMA_TAU_GEV, evaluate_tree,
)


class NeutralTreeTauTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = evaluate_tree(order=10)

    def test_exact_four_card_source_scope(self):
        self.assertEqual(tuple(self.result["cards"]), CARD_IDS)
        self.assertAlmostEqual(GAMMA_TAU_GEV, 2.267351e-12, delta=1e-17)

    def test_nonnegative_exact_and_contact_close(self):
        for card in self.result["cards"].values():
            for channel in card["channels"].values():
                exact, contact = channel["tree_h_H_A_width_GeV"], channel["tree_h_H_A_contact_width_GeV"]
                self.assertTrue(math.isfinite(exact))
                self.assertTrue(math.isfinite(contact))
                self.assertGreaterEqual(exact, 0)
                self.assertGreaterEqual(contact, 0)
                self.assertAlmostEqual(exact / GAMMA_TAU_GEV, channel["tree_h_H_A_BR"])
                if contact:
                    self.assertLess(abs(exact / contact - 1), 0.01)

    def test_dipole_and_tree_not_summed(self):
        self.assertEqual(self.result["physical_lfv"], "UNKNOWN")
        self.assertIsNone(self.result["global_acceptance"])
        for c in self.result["cards"].values():
            for ch in c["channels"].values():
                self.assertIsNone(ch["coherent_total_BR"])
                self.assertIsNone(ch["physical_threebody_BR"])
                self.assertGreater(ch["partial_zee_dipole_only_BR"], 0)

    def test_invalid_quadrature_order(self):
        for order in (-1, 0, 1, 7, 49, 2.0, "12"):
            with self.assertRaises(ValueError):
                evaluate_tree(order=order)


if __name__ == "__main__":
    unittest.main()
