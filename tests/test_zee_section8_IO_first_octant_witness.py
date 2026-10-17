"""Regression on independent first-octant family-Z2 neutrino witness."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_IO_first_octant_witness import (
    WITNESS,STATUS,FIRST_OCTANT_PROVISIONAL,
    evaluate_coordinates,exploratory_objective,
)
class TestFirstOctantWitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row=evaluate_coordinates(
            WITNESS["coordinates"],tanbeta=WITNESS["tanbeta"])
    def test_four_source_marginal_2sigma_windows(self):
        x=self.row
        self.assertTrue(x[
            "four_2022_upper_octant_table1_other_observables_2sigma"])
        for key,residual in x[
            "four_2022_table1_residuals_in_source_sigma"].items():
            with self.subTest(key=key):
                self.assertLess(abs(residual),2.001)
    def test_first_octant_witness_not_upper_octant(self):
        x=self.row
        self.assertTrue(x[
            "theta23_first_octant_exploratory_0p43_to_0p49"])
        self.assertGreater(x["oscillation_observables"]["sin2theta23"],
                           FIRST_OCTANT_PROVISIONAL[0])
        self.assertLess(x["oscillation_observables"]["sin2theta23"],
                           FIRST_OCTANT_PROVISIONAL[1])
        self.assertLess(x["oscillation_observables"]["sin2theta23"],.5)
    def test_mass_sum_and_ratio_with_historical_cut(self):
        x=self.row
        self.assertTrue(x["historical_sum_mnu_lt_0p13_eV"])
        self.assertTrue(x["reported_IO_ratio_2_to_15"])
        self.assertAlmostEqual(x["oscillation_observables"]["sum_masses_eV"],
                               .106199,places=4)
        self.assertAlmostEqual(x["IO_m1_over_m3"],8.606,places=2)
    def test_charged_lepton_mass_closure_and_physical_texture(self):
        x=self.row
        self.assertLess(x["charged_mass_closure_max_GeV"],1e-9)
        self.assertGreater(x["charged_texture_e_minus_mmu_GeV"],0)
        self.assertLess(x["charged_texture_e_minus_mmu_GeV"],.001)
        self.assertTrue(x[
            "passes_EXPLORATORY_four_plus_theta23_window_and_history"])
        self.assertAlmostEqual(exploratory_objective(
            WITNESS["coordinates"],WITNESS["tanbeta"]),0,places=5)
    def test_prevents_unjustified_allowed_or_nufit_claims(self):
        x=self.row
        self.assertIn("NOT_SOURCE_LIKELIHOOD_OR_ALLOWED",STATUS)
        self.assertFalse(x["theta23_first_octant_source_likelihood_validated"])
        self.assertEqual(x["source_2022_full_5observable_2sigma_pass"],
                         "NOT_EVALUATED")
        self.assertFalse(x["full_NuFIT_likelihood"])
        self.assertFalse(x["full_LFV_likelihood"])
        self.assertEqual(x["high_tanbeta_scalar_theory_screen"],
                         "NOT_EVALUATED")
        self.assertIsNone(x["full_Zee_allowed"])
if __name__=="__main__":
    unittest.main()
