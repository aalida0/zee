import tempfile
import unittest
import math
from pathlib import Path
from research.full_constraints.bsgamma_flavio_2026 import np_remainder_budget as m

class FullTwoScalarBScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.data=m.run(Path(cls.tmp.name)/"test.json")
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_2026_published_range_and_no_calibrated_NP_sigma(self):
        d=self.data
        self.assertEqual(d["n_original_certified_scalar_points"],16)
        self.assertEqual(d["source_2026"].split()[0],"arXiv:2608.29863v1")
        self.assertFalse(d["full_B_uncertainty_completed"])
        self.assertEqual(d["physical_B"],"UNKNOWN")
        self.assertIsNone(d["global_acceptance"])
        self.assertLess(d["two_sided_gaussian_95_lower"],3.54e-4)
        self.assertGreater(d["two_sided_gaussian_95_upper"],3.54e-4)
        for row in d["spectra"]:
            self.assertIsNone(row["NP_remainder_certified_bound"])
            self.assertIsNone(row["NP_theory_sigma"])
            self.assertIsNone(row["global_acceptance"])
            self.assertGreater(row["2026_positive_missing_branching_shift_headroom"],0)
            self.assertGreater(row["2026_relative_positive_shift_headroom_to_LO_NP"],0)

    def test_flavio_exact_quadratic_decomposition_and_no_baseline_transfer(self):
        for r in self.data["spectra"]:
            s=r["old_scheme_flavio_odd_even_signed_split"]
            self.assertAlmostEqual(
                s["old_backend_full_plus"]-s["old_backend_SM"],
                s["NP_linear_odd"]+s["NP_quadratic_even"],
                delta=1e-11
            )
            self.assertLess(abs(s["doubled_odd_residual"]),1e-12)
            self.assertLess(abs(s["doubled_even_residual"]),1e-12)
            self.assertFalse(s["NP_quadratic_has_been_transferred_to_2026"])
            self.assertFalse(r["published_full_2026_NNLO_rate_executed"])

    def test_single_state_M670_is_not_false_2026_NNLO_likelihood(self):
        r=self.data["one_state_670_full_NNLO_vs_LO_NP_control"]
        self.assertEqual(r["mHplus_GeV"],670.)
        self.assertEqual(r["tanbeta"],50.)
        self.assertIsNone(r["conversion_to_theory_sigma"])
        self.assertFalse(r["source_bound_uses_same_approximate_likelihood"])
        self.assertFalse(r["allowed_to_transfer_published_bound_directly_to_Zee"])
        self.assertTrue(math.isfinite(r["LO_NP_Eq4_gaussian_pull"]))

if __name__=="__main__":unittest.main()
