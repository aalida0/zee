import unittest, tempfile
from pathlib import Path
from research.full_constraints.bsgamma_2026_source_gate import published_order_95 as q

class ZeeB2026PublishedOrderScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.data=q.run(Path(cls.tmp.name)/"b95.json")
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_two_distinct_statistics_2017_confidence_placement(self):
        self.assertEqual(self.data["n_original_source_certified_scalar_spectra"],16)
        self.assertEqual(self.data["n_LO_NP_95_one_sided_inside"],10)
        self.assertEqual(self.data["n_LO_NP_95_two_sided_inside"],16)
        r={x["scalar_id"]:x for x in self.data["scalar_rows"]}
        self.assertTrue(r[15673]["one_sided_95_LO_NP_screen"])
        self.assertFalse(r[15591]["one_sided_95_LO_NP_screen"])
        self.assertFalse(r[2264]["one_sided_95_LO_NP_screen"])
        self.assertTrue(r[15673]["two_sided_95_LO_NP_screen"])
        self.assertTrue(r[15591]["two_sided_95_LO_NP_screen"])

    def test_adopt_only_source_defined_order(self):
        self.assertTrue(self.data["source_order_2026_LO_NP_constraint_usable_for_phenomenology"])
        self.assertTrue(self.data["2026_TypeII_one_state_670GeV_limit_directly_inapplicable_to_two_state_Zee"])
        self.assertTrue(self.data["statistical_screen_is_published_approximation_not_author_reproduced_FC"])
        self.assertIsNone(self.data["global_acceptance"])
        self.assertEqual(self.data["physical_full_95CL"],"UNKNOWN")
        for v in self.data["scalar_rows"]:
            self.assertIsNone(v["NP_missing_high_order_absolute_remainder_certified_bound"])
            self.assertIsNone(v["physical_full_model_95_cl_exclusion"])
            self.assertIsNone(v["global_acceptance"])
            self.assertFalse(v["full_NNLO_model_rate_computed"])

if __name__=="__main__":unittest.main()
