"""Check historical 2022 acceptance logic and input reliability.

Tests intentionally do not mistake five independent 2sigma intervals,
descriptive IO mass ratios or historical cosmology for a
current NuFIT/LFV/full-Zee allowed benchmark.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_2022_2sigma_acceptance import (
    STATUS, SOURCE, source_acceptance, parse_floats, parse_seeds,
    one_run, DEFAULT_BOUNDS,
)

class TestZee2022Acceptance(unittest.TestCase):
    def test_near_charged_tau_endpoint_is_not_excluded_by_old_bounds(self):
        self.assertGreater(DEFAULT_BOUNDS[1][1],12.)
        self.assertIn("NOT_NUFIT_OR_ALLOWED",STATUS)

    def test_source_2sigma_acceptance_and_cosmo_and_IO_mass_ratio(self):
        target={k:val[0] for k,val in SOURCE.items()}
        target.update(masses_eV=[.052,.0528,.018],
                      sum_masses_eV=.1228)
        acc=source_acceptance(target)
        self.assertTrue(acc["oscillation_5of5_2sigma"])
        self.assertTrue(acc["historical_Planck_BAO_sum_lt_0p13_eV"])
        self.assertTrue(acc["source_reported_2_to_15"])
        self.assertTrue(acc["source_style_all_three_conditions"])
        self.assertAlmostEqual(
            acc["source_acceptance_proxy_objective_NOT_chi2"],0.)

    def test_source2sigma_central_mismatch_can_still_pass(self):
        target={k:val[0] for k,val in SOURCE.items()}
        # +1.9 sigma from source central IS accepted by source window.
        target["sin2theta12"]+=1.9*SOURCE["sin2theta12"][2]
        target.update(masses_eV=[.052,.0528,.018],
                      sum_masses_eV=.1228)
        self.assertTrue(source_acceptance(target)[
            "source_style_all_three_conditions"])

    def test_failures_do_not_claim_allowed(self):
        target={k:val[0] for k,val in SOURCE.items()}
        target.update(masses_eV=[.05,.051,.00001],
                      sum_masses_eV=.10101)
        self.assertFalse(source_acceptance(target)[
            "source_style_all_three_conditions"])
        target["sin2theta12"]+=5*SOURCE["sin2theta12"][2]
        self.assertFalse(source_acceptance(target)[
            "oscillation_5of5_2sigma"])

    def test_parse_input(self):
        self.assertEqual(parse_floats("10,15"),[10.,15.])
        self.assertEqual(parse_seeds("11,22"),[11,22])
        with self.assertRaises(ValueError):parse_floats("10,10")
        with self.assertRaises(ValueError):parse_seeds("11,11")

    def test_tiny_optimizer_only_reports_a_historical_texture_diagnostic(self):
        r=one_run(tanbeta=15.,seed=11,maxiter=1,popsize=3)
        self.assertIsNone(r["physical_Zee_allowed"])
        self.assertEqual(r["full_LFV"],"NOT_EVALUATED")
        self.assertEqual(r["current_NuFIT_correlated_likelihood"],
                         "NOT_EVALUATED")
        self.assertLess(r["charged_mass_closure_max_GeV"],1e-9)
        self.assertIn("source_acceptance_proxy_objective_NOT_chi2",r)

if __name__=="__main__":
    unittest.main()
