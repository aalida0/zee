import unittest
import math
from pathlib import Path
from research.full_constraints.scan_pilot_2026 import lfv_coherent_ledger_budget as a


class SourceLockedCoherentLFVBudgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v=a.evaluate_ledger()

    def test_source_and_global_scope_are_not_promoted(self):
        self.assertEqual(self.v["full_physical_lfv"], "UNKNOWN")
        self.assertIsNone(self.v["global_acceptance"])
        self.assertIsNone(self.v["channels"]["mu_to_e_gamma"]["actual_missing_norm_bound"])
        self.assertTrue(self.v["source_retained_ledger_only"])

    def test_channel_coherent_component_sums(self):
        for name,z in self.v["channels"].items():
            self.assertAlmostEqual(
                z["source_included_BR"]/z["signed_ledger_reconstructed_BR"],1,
                places=8,
            )
            self.assertIn("one_loop_singlet_FdagF",z["included_groups"])
            self.assertIn("two_loop_neutral_fermion_photon",z["included_groups"])
            self.assertGreater(z["limit_coefficient_norm_GeV_minus2"],0)
            self.assertGreater(z["sum_group_norm_to_limit"],0)
            self.assertEqual(len(z["missing_group_names"]),7)

    def test_saved_benchmark_mu_egamma_small_without_importing_bars(self):
        mu=self.v["channels"]["mu_to_e_gamma"]
        self.assertTrue(math.isclose(
            mu["source_included_BR"],4.7468329803506013e-23,rel_tol=1e-9))
        self.assertGreater(mu["headroom_for_missing_total_vector_GeV_minus2"],0)
        self.assertTrue(mu["hypothetical_K_is_not_a_bound"])


if __name__=="__main__":
    unittest.main()
