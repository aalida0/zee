import math
import unittest

from research.full_constraints.scan_pilot_2026 import h125_b_shortlist_2264 as x


class NewZee2264HiggsAndBTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=x.evaluate()

    def test_the_same_source_card_and_near_alignment_not_a_full_higgs_fit(self):
        v=self.r
        self.assertEqual(v["scalar_sha256"],
                         "49d468ccfd1262ea2900ac41479071e821475f854c3b13441130c6a289417c8e")
        self.assertGreater(v["h125_coupling_ratios"]["kappa_V"],0.99)
        self.assertIsNone(v["h125_total_width"])
        self.assertEqual(v["full_higgs"],"UNKNOWN")
        self.assertIsNone(v["global_acceptance"])

    def test_photon_source_rates_and_denominator_free_ratios(self):
        v=self.r
        for s in ("h125_gammagamma","h125_Zgamma"):
            z=v[s]
            self.assertTrue(math.isfinite(z["ratio_to_SM"]))
            self.assertGreater(z["leading_one_loop_width_GeV"],0)
            self.assertGreater(z["matched_SM_leading_one_loop_width_GeV"],0)
        kv=v["h125_coupling_ratios"]["kappa_V"]
        self.assertAlmostEqual(v["h125_width_independent_ratios"]["VBF_gammagamma_over_VBF_WW"],
                               v["h125_gammagamma"]["ratio_to_SM"]/kv**2,places=13)
        self.assertTrue(v["h125_width_independent_ratios"]["total_h125_width_cancels"])

    def test_b_reference_is_diagnostic_and_original_class_not_promoted(self):
        b=self.r["B_to_Xs_gamma"]
        self.assertEqual(b["approx_classification"],"APPROX_COMPATIBLE")
        self.assertEqual(b["physical_classification"],"UNKNOWN")
        self.assertIsNone(b["model_NP_uncertainty"])
        self.assertIsNone(b["physical_exclusion"])
        self.assertGreater(b["rate_linear_diagnostic"],0)
        self.assertTrue(math.isfinite(b["conditional_pull"]))
        self.assertEqual(self.r["physical_B"],"UNKNOWN")


if __name__=="__main__":
    unittest.main()
