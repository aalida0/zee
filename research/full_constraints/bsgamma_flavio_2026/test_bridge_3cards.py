import unittest
import math

from research.full_constraints.bsgamma_flavio_2026 import bridge_3cards as b

class ThreeZeeScalarFlavioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pathlib import Path
        import tempfile
        cls.tmp=tempfile.TemporaryDirectory()
        cls.data=b.run(Path(cls.tmp.name)/"results.json")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_complete_replay_result_is_explicitly_conditional(self):
        self.assertEqual(self.data["n_case"],3)
        self.assertEqual(self.data["flavio_version"],"2.7.1")
        self.assertIsNone(self.data["global_acceptance"])
        self.assertEqual(self.data["full_B_physics"],"UNKNOWN")
        self.assertTrue(self.data["no_complete_NLO_C4_C1toC6"])

    def test_matching_identities_and_nonzero_order_effect(self):
        self.assertEqual({x["scalar_id"] for x in self.data["cases"]},{15591,15673,2264})
        for row in self.data["cases"]:
            self.assertGreater(row["flavio_lo_C7C8_NP_rate"],0)
            self.assertGreater(row["flavio_LOplusNLO_C7C8_only_rate"],0)
            self.assertNotEqual(row["difference_NLOdipoleOnly_minus_LO"],0.0)
            self.assertFalse(row["NLO_C4_inserted_into_flavio"])
            self.assertIsNone(row["Zee_NP_theory_sigma"])
            self.assertIsNone(row["B_physical_exclusion"])
            self.assertEqual(row["physical_B"],"UNKNOWN")

    def test_source_same_sm_base_and_reference_spectrum(self):
        rates={row["flavio_SM_rate"] for row in self.data["cases"]}
        self.assertEqual(len(rates),1)
        self.assertGreater(min(rates),3e-4)
        self.assertLess(max(rates),3.9e-4)
        self.assertTrue(all(math.isfinite(v) for row in self.data["cases"]
                            for v in row["ordinary_bmu_matching"].values()))

if __name__=="__main__":
    unittest.main()
