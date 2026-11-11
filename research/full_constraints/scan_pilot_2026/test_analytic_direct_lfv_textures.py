import unittest
import numpy as np
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.scan_pilot_2026 import analytic_direct_lfv_textures as a


class ZeeLinearTextureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p={x["id"]:x for x in source_points()}

    def test_minimum_norm_complex_constraints_close(self):
        row=a.build(self.p[15591],"NO",20261111)
        self.assertEqual(row["linear_constraint_rank_complex"],2)
        self.assertEqual(row["remaining_direct_Yukawa_nullity_complex"],2)
        self.assertLess(max(row["direct_D_e_mu"],row["direct_D_mu_e"]),1e-10)
        self.assertLess(row["neutrino_closure"],2e-9)
        self.assertLess(row["residual_complex_direct_D"],1e-10)
        self.assertEqual(row["physical_LFV"],"UNKNOWN")
        self.assertIsNone(row["global_acceptance"])
        self.assertIsNotNone(row["partial_mu_to_e_gamma_BR"])

    def test_origins_and_uncertainty_not_promoted(self):
        self.assertEqual(a.IDS,(15591,15673))
        self.assertEqual(a.ORDERINGS,("NO","IO"))
        self.assertEqual(a.SEEDS,(20261111,20261112))
        self.assertIsNone(self.p[15591]["global_acceptance"])
        self.assertEqual(self.p[15673]["gates"]["vacuum"]["assessment"],"PASS")


if __name__=="__main__":
    unittest.main()
