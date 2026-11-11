import unittest
import tempfile
from pathlib import Path
from research.full_constraints.bsgamma_flavio_2026 import published_eq4_triangulation as m

class Misiak2026ZeeCrosscodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=tempfile.TemporaryDirectory()
        cls.r=m.run(Path(cls.d.name)/"16_central_checks.json")
    @classmethod
    def tearDownClass(cls):cls.d.cleanup()

    def test_published_2026_input_and_source_match(self):
        self.assertEqual(self.r["n_spectra"],16)
        self.assertEqual(self.r["published_source"],"2608.29863v1")
        self.assertEqual(self.r["published_2026_SM_branching_fraction"],3.54e-4)
        self.assertTrue(self.r["published_2HDMII_mHplus_bound_is_not_direct_Zee_two_state_cut"])
        for row in self.r["scalars"]:
            self.assertAlmostEqual(row["legacy_2026_diagnostic_pull"],
                                   row["published_2026_Eq4_pull"],delta=5e-10)

    def test_published_eq4_and_independent_flavio_are_not_interchangeable(self):
        cases={x["scalar_id"]:x for x in self.r["scalars"]}
        self.assertEqual(set((15591,15673,2264)).intersection(cases),{15591,15673,2264})
        self.assertNotEqual(cases[15591]["heuristic_transferred_LO_pull"],
                            cases[15591]["published_2026_Eq4_pull"])
        for c in self.r["scalars"]:
            self.assertFalse(c["NLO_C4_inserted_in_flavio"])
            self.assertTrue(c["flavio_original_SM_prediction"]<m.PUBLISHED_SM)
            self.assertIsNone(c["full_model_exclusion"])
            self.assertEqual(c["physical_B"],"UNKNOWN")
            self.assertIsNone(c["NP_quadratic_remainder_bound"])
            self.assertIsNone(c["NP_model_theory_uncertainty"])
            self.assertIsNone(c["global_acceptance"])
        self.assertEqual(self.r["physical_B"],"UNKNOWN")
        self.assertIsNone(self.r["global_acceptance"])

if __name__=="__main__":unittest.main()
