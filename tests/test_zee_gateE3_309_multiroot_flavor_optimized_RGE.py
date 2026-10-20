"""E3 309 original spectra: synthetic B2/D1/D2/D4/RGE end-to-end tests.

The tests verify source schemas, partial-physics labels and resumability.
They do NOT replace AF execution of the complete 309-spectrum study.
"""
import csv
import ast
import inspect
import textwrap
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateE3_309_multiroot_flavor_optimized_RGE as e


class E3Contracts(unittest.TestCase):
    def test_B2_trials_first_original_neutrino_family(self):
        def fake_solver(p,M,f,rng,strength):
            return {
                "candidate_id":p["id"],
                "status":"NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED",
                "neutrino_matrix_closure_eV":0.,
                "partial_LFV_score_NOT_EXCLUSION":
                    1e-5 if strength==0. else .001,
            }
        with patch.object(e,"solve_point",side_effect=fake_solver),\
             patch.object(e,"f_from_null_parameter",
                          return_value=np.zeros((3,3))):
            roots,stats=e.try_B2_family(
                {"id":"B4_TEST"},np.random.default_rng(42),
                np.eye(3),np.zeros((3,3)),300,5)
        self.assertEqual(stats["attempted"],300)
        self.assertEqual(stats["closed_and_perturbative"],300)
        self.assertEqual(len(roots),5)
        self.assertEqual(stats["original_E1_rank1_partial_score"],1e-5)
        self.assertTrue(all(x["status"]==
            "NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED" for x in roots))

    def test_B2_seed_failure_is_fatal_not_scientific_exclusion(self):
        with patch.object(e,"solve_point",return_value=None):
            with self.assertRaisesRegex(ValueError,"seed texture"):
                e.try_B2_family({"id":"B4_TEST"},np.random.default_rng(42),
                                np.eye(3),np.zeros((3,3)),300,5)

    def test_complete_one_original_point_joint_path_is_consistent(self):
        p={"id":"B4_TEST","mH1":300.,"mH2":700.,
           "gamma":1.0,"beta":1.1,"alpha":1.2}
        start={"original_E1_rank1_partial_score":.003,"attempted":300,
               "closed_and_perturbative":300,"saved":5,
               "discarded_or_failed":0}
        sols=[{"candidate_id":"B4_TEST","status":
               "NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED"} for _ in range(5)]
        def d1(point,solution,rank):
            return {"candidate_id":"B4_TEST",
                    "joint_incomplete_LFV_score_NOT_EXCLUSION":.02+rank*.001}
        def optimizer(point,root,baseline,max_evals):
            score=baseline["joint_incomplete_LFV_score_NOT_EXCLUSION"]
            return {"seed_original_score":score,"best_score":score/2.,
                    "solution":{"f":{"real":[[0.]*3]*3,
                                      "imag":[[0.]*3]*3},
                                "Y":{"real":[[0.]*3]*3,
                                      "imag":[[0.]*3]*3}}}
        with patch.object(e,"try_B2_family",return_value=(sols,start)),\
             patch.object(e,"candidate_flavor",side_effect=d1),\
             patch.object(e,"optimize_start",side_effect=optimizer),\
             patch.object(e,"compare_partial",
                          side_effect=lambda p,f,Y,opt:{
                              "new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION":
                                  opt["best_score"]*1.2}),\
             patch.object(e,"original_yukawa_RGE",
                          return_value={
                            "sampled_BFB_and_55channel_unitarity_pass_to_10TeV":
                                True}) as check:
            row=e.analyze(
                p,{"single_B2_partial_LFV_score_NOT_EXCLUSION":.003},
                None,np.eye(3),np.zeros((3,3)),np.random.default_rng(2),
                300,5,2,240,None,24)
        self.assertEqual(row["diagnostic_status"],
            "MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED")
        self.assertTrue(check.called)
        self.assertEqual(row["D2"]["number_optimized_family_starts"],2)
        self.assertIsNone(row["full_Zee_allowed_or_excluded"])
        self.assertFalse(row["complete_neutrino_LFV_likelihood_available"])

    def test_live_D2_D4_C1_C4_result_field_names(self):
        """Inspect actual source dictionaries rather than copying a mock typo."""
        from zee_gateD2_neutrino_exact_partial_LFV_optimization import (
            optimize_start)
        from zee_gateD4_W_photon_barr_zee_27 import compare_partial
        from zee_gateC4_running_55channel_unitarity import full_trajectory
        from zee_gateC1_joined_uv_pilot import build_model_state
        def keys(fn):
            node=ast.parse(textwrap.dedent(inspect.getsource(fn)))
            # Real build_model_state returns (state, {checks}), rather
            # than returning a dict directly; inspect dict literals nested
            # anywhere in each return expression, including tuple items.
            dictionaries=[d for z in ast.walk(node)
                          if isinstance(z,ast.Return) and z.value is not None
                          for d in ast.walk(z.value) if isinstance(d,ast.Dict)]
            return {x.value for d in dictionaries for x in d.keys
                    if isinstance(x,ast.Constant) and isinstance(x.value,str)}
        self.assertTrue({
            "seed_original_score","best_score","solution",
            "D1_crosschecked_LFV"} <= keys(optimize_start))
        self.assertTrue({
            "new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION"}
                        <= keys(compare_partial))
        self.assertTrue({
            "first_tree_unitarity_uncertified_scale_GeV",
            "maximum_scattering_eigenvalue_encountered",
            "tree_unitarity_8pi_at_all_sampled_steps",
            "BFB_sufficient_at_all_sampled_steps",
            "reached_end_scale","BFB_negative_witness","status"
        }<=keys(full_trajectory))
        self.assertTrue({"neutrino_matrix_closure_eV"}<=keys(build_model_state))

    def test_checkpoint_fails_on_duplicate_or_physical_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint=Path(tmp)/"checkpoint.jsonl"
            x={"candidate_id":"B4_A","full_Zee_allowed_or_excluded":None}
            checkpoint.write_text(json.dumps(x)+"\n")
            self.assertEqual(len(e.load_checkpoint(checkpoint,{"B4_A"})),1)
            checkpoint.write_text(json.dumps(x)+"\n"+json.dumps(x)+"\n")
            with self.assertRaisesRegex(ValueError,"Duplicated"):
                e.load_checkpoint(checkpoint,{"B4_A"})
            checkpoint.write_text(json.dumps({
                **x,"full_Zee_allowed_or_excluded":True})+"\n")
            with self.assertRaisesRegex(ValueError,"Duplicated"):
                e.load_checkpoint(checkpoint,{"B4_A"})

    def test_finalize_309_source_cohort_not_an_allowed_population(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            raw={}
            for i in range(309):
                name=f"B4_{i:07d}"
                raw[name]={
                    "id":name,"mH1":"300","mH2":"700",
                    "gamma":"1.0","beta":"1.2",
                    "production_weighted_nonleptonic_cascade_upper_proxy":
                        ".65"}
            result={name:{
                "candidate_id":name,
                "diagnostic_status":
                    "INSUFFICIENT_SAVED_B2_FAMILIES_NOT_PHYSICAL_EXCLUSION",
                "full_Zee_allowed_or_excluded":None}
                for name in raw}
            summary=e.finalize(
                out,list(raw.values()),result,{"byid":raw},
                {"neutrino_trials":300})
            self.assertEqual(summary["E2_original_no_deeper_witness_cohort"],309)
            self.assertEqual(summary["B2_insufficient_family_spectra"],309)
            self.assertIsNone(summary[
                "NO_complete_experimental_Zee_allowed_or_excluded"])
            self.assertTrue((out/
                "E3_all_309_multi_neutrino_partial_LFV_diagnostics.jsonl").exists())

    def test_live_source_exports_checked_not_mocks(self):
        from gateB2_zee_neutrino_family_scan import solve_point
        from zee_gateD1_joint_300_neutrino_lfv_inventory import candidate_flavor
        from zee_gateD2_neutrino_exact_partial_LFV_optimization import (
            optimize_start, optimize_kernels_cache)
        from zee_gateD4_W_photon_barr_zee_27 import compare_partial
        from zee_gateC4_running_55channel_unitarity import full_trajectory
        for x in (solve_point,candidate_flavor,optimize_start,compare_partial,
                  optimize_kernels_cache,full_trajectory):
            self.assertTrue(callable(x))
        self.assertIn("allowed",e.BLOCKED.lower())
        self.assertIn("NOT_ALLOWED",e.STATUS)


if __name__=="__main__":
    unittest.main()
