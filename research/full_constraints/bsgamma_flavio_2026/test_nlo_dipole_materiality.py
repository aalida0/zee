import unittest
import tempfile
import math
from pathlib import Path
from research.full_constraints.bsgamma_flavio_2026 import nlo_dipole_materiality as m

class StrictNloMatchingMaterialityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.report=m.run(Path(cls.tmp.name)/"result.json")
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_model_scope_is_not_promoted(self):
        self.assertEqual(self.report["n_spectra"],16)
        self.assertFalse(self.report["NLO_C4_included"])
        self.assertFalse(self.report["NLO_matrix_elements_included"])
        self.assertEqual(self.report["physical_B"],"UNKNOWN")
        self.assertIsNone(self.report["global_acceptance"])
        self.assertIsNone(self.report["claimed_theory_error"])
        for row in self.report["two_state_spectra"]:
            self.assertFalse(row["NLO_C4_included"])
            self.assertFalse(row["NNLO_2026_implementation"])
            self.assertFalse(row["NLO_matrix_elements_consistently_updated"])
            self.assertTrue(math.isfinite(row["signed_NLO_dipole_matching_only_shift"]))
            self.assertIsNone(row["NP_uncertainty_sigma"])

    def test_one_state_670_cannot_be_used_as_model_likelihood_calibration(self):
        p=self.report["one_state_670_reference"]
        self.assertEqual(p["source_full_order_published_bound_GeV"],670.)
        self.assertTrue(p["NLO_dipole_only_not_full_NNLO"])
        self.assertTrue(p["one_state_NLO_only_does_not_calibrate_NP_uncertainty"])
        self.assertLess(p["one_state_at_published_mass"]["NLO_dipole_matching_inserted_into_Eq4"],
                        p["one_state_at_published_mass"]["LO_NP_Eq4"])

if __name__=="__main__":unittest.main()
