import math
import unittest

from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_mixed_flavour_tree import (
    CHANNELS, evaluate
)


class TauMixedTreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = evaluate(10)

    def test_source_complete_and_not_physical(self):
        self.assertEqual(list(self.result['cards']), ['D7_NO','D7_IO','F13_NO','F13_IO'])
        self.assertEqual(self.result['physical_lfv'], 'UNKNOWN')
        self.assertIsNone(self.result['global_acceptance'])

    def test_two_distinct_flavour_channels(self):
        self.assertEqual(len(CHANNELS), 2)
        for card in self.result['cards'].values():
            self.assertEqual(set(card['channels']), {x[0] for x in CHANNELS})
            for row in card['channels'].values():
                self.assertGreater(row['neutral_h_H_A_exact_tree_BR'],0.)
                self.assertTrue(math.isfinite(row['neutral_h_H_A_exact_tree_BR']))
                self.assertIsNone(row['physical_threebody_BR'])
                self.assertIsNone(row['coherent_full_LFV_amplitude'])
                self.assertLess(abs(row['neutral_h_H_A_exact_tree_width_GeV']/row['neutral_h_H_A_contact_width_GeV']-1.), 0.01)

    def test_invalid_quadrature_orders(self):
        for order in (0,7,49,-1,10.,'10'):
            with self.assertRaises(ValueError): evaluate(order)


if __name__ == '__main__':
    unittest.main()
