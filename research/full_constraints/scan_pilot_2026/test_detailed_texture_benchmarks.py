import unittest
from research.full_constraints.scan_pilot_2026 import detailed_texture_benchmarks as d
from research.full_constraints.scan_pilot_2026.vacuum_followup import strict_inputs

class DetailedTextureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scalar={p["id"]:p for p in strict_inputs()}
    def test_d4_and_neutrino_and_mu3e_replay(self):
        a=d.detailed((284,"IO",4,0.),self.scalar[284])
        self.assertEqual(a["original_B_approx_diagnostic"]["class"],"APPROX_COMPATIBLE")
        self.assertEqual(a["original_vacuum_status"],"UNKNOWN")
        self.assertLess(a["partial_mu_to_e_gamma_BR"],d.MEG_II)
        self.assertLess(a["neutrino_residual"],2e-9)
        self.assertIsNone(a["globally_allowed"])
        self.assertIsNone(a["production_cross_section_pb"])
        self.assertEqual(a["partial_mu_to_3e_tree_scope"],"PASS")
        self.assertTrue(0<a["BR_H2_H1Z_tree"]<1)
        self.assertTrue(0<a["BR_H1_tb_tree"]<1)
    def test_invalid_order_or_unplanned_eta_fails(self):
        with self.assertRaises(ValueError):
            d.detailed((284,"NO",0,0.002),self.scalar[284])

if __name__=="__main__":
    unittest.main()
