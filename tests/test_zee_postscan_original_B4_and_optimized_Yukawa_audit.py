"""Postscan original-potential and optimized-Yukawa audit contracts.

Synthetic fixtures validate source integrity and score comparability only.
They are NOT tests of an experimental Zee exclusion likelihood.
"""
import math
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_postscan_original_B4_and_optimized_Yukawa_audit as p


class PostscanContracts(unittest.TestCase):
    def test_same_objective_improvement_not_B2_score(self):
        d1={"B4_A":8.,"B4_B":10.}
        d2=[
          {"candidate_id":"B4_A",
           "original_D1_best_partial_score_NOT_EXCLUSION":8.,
           "new_best_partial_score_NOT_EXCLUSION":.02},
          {"candidate_id":"B4_B",
           "original_D1_best_partial_score_NOT_EXCLUSION":10.,
           "new_best_partial_score_NOT_EXCLUSION":2.}]
        result=p.compare_same_objective(d1,d2)
        self.assertAlmostEqual(result["B4_A"][
            "D1_over_D2_partial_score_improvement_factor"],400.)
        self.assertAlmostEqual(result["B4_B"][
            "D1_over_D2_partial_score_improvement_factor"],5.)
        self.assertTrue(result["B4_A"][
            "both_scores_are_INCOMPLETE_LFV_NOT_a_likelihood"])

    def test_false_improvement_and_drift_rejected(self):
        reference={"B4_A":.8}
        with self.assertRaisesRegex(ValueError,"worsened"):
            p.compare_same_objective(reference,[{
                "candidate_id":"B4_A",
                "original_D1_best_partial_score_NOT_EXCLUSION":.8,
                "new_best_partial_score_NOT_EXCLUSION":1.2}])
        with self.assertRaisesRegex(ValueError,"baseline objective mismatch"):
            p.compare_same_objective(reference,[{
                "candidate_id":"B4_A",
                "original_D1_best_partial_score_NOT_EXCLUSION":.2,
                "new_best_partial_score_NOT_EXCLUSION":.1}])

    def test_duplicate_missing_and_negative_rejected(self):
        good={
            "candidate_id":"B4_A",
            "original_D1_best_partial_score_NOT_EXCLUSION":1.2,
            "new_best_partial_score_NOT_EXCLUSION":.9}
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            p.compare_same_objective({"B4_A":1.2},[good,good])
        with self.assertRaisesRegex(ValueError,"absent"):
            p.compare_same_objective({},[good])
        with self.assertRaisesRegex(ValueError,"positive"):
            p.compare_same_objective({"B4_A":1.2},
                [{**good,"new_best_partial_score_NOT_EXCLUSION":-.2}])
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            p.compare_same_objective({"B4_A":1.2},
                [{**good,"new_best_partial_score_NOT_EXCLUSION":float("nan")}])

    def test_numerical_RGE_two_resolution_requires_consistency(self):
        def make(reach=True,bfb=True,uni=True,neg=False):
            return {
                "status":"COMPLETE_TO_10TEV" if reach else "STOPPED_BY_SOURCE",
                "reached_end_scale":reach,
                "BFB_sufficient_at_all_sampled_steps":bfb,
                "tree_unitarity_8pi_at_all_sampled_steps":uni,
                "BFB_negative_witness":neg,
                "first_BFB_uncertified_scale_GeV":None,
                "first_tree_unitarity_uncertified_sample_GeV":None,
                "maximum_scattering_eigenvalue_encountered":12.3}
        with patch(
           "zee_gateC4_running_55channel_unitarity.full_trajectory",
           side_effect=[make(),make()]):
            ok=p.running_result("mock",None,None,700.,24,None)
        self.assertTrue(ok[
            "passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV"])
        with patch(
           "zee_gateC4_running_55channel_unitarity.full_trajectory",
           side_effect=[make(),make(uni=False)]):
            mismatch=p.running_result("mock",None,None,700.,24,None)
        self.assertEqual(mismatch["status"],
                         "COARSE_REFINED_DISAGREEMENT_INCONCLUSIVE")
        self.assertFalse(mismatch[
            "passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV"])
        with patch(
           "zee_gateC4_running_55channel_unitarity.full_trajectory",
           side_effect=[make(reach=False,uni=False),make(reach=False,uni=False)]):
            fail=p.running_result("mock",None,None,700.,24,None)
        self.assertFalse(fail[
            "passes_sampled_running_BFB_and_55channel_unitarity_to_10TeV"])

    def test_no_global_exclusion_can_be_encoded_as_status(self):
        self.assertIn("NOT_ALLOWED",p.STATUS)
        self.assertIn("NOT_ALLOWED",p.BLOCKED)
        self.assertIn("global_vacuum_proof",p.MISSING)
        self.assertEqual(p.MISSING["complete_Zee_HiggsTools_adapter"],
                         "NOT_IMPLEMENTED")


if __name__=="__main__":
    unittest.main()
