"""E1 original-B4 5,557-point funnel integrity and ranking tests.

These synthetic fixtures are NOT 10-TeV source RGE or vacuum physics.
The real AF campaign must use a Q4v13-pinned generator and 5,557
archived scalar/EWPO-screened B4 records.
"""
from __future__ import annotations

import csv
import ast
import inspect
import textwrap
import json
import math
from pathlib import Path
from unittest.mock import patch
import numpy as np
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateE1_original_5557_running_funnel as e


class E1IntegrityContract(unittest.TestCase):
    def fixture(self):
        row={"id":"B4_0006862",
             "candidate_status":"SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"}
        row.update({k:1. for k in e.KEYS})
        row.update({
            "production_weighted_nonleptonic_cascade_upper_proxy":.65,
            "chi2_Gfitter":.15,
            "max_unitarity":11.0})
        return row

    def test_B4_source_parser_requires_real_fields_and_not_allowed_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"data.csv"
            row=self.fixture()
            with file.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(row))
                w.writeheader()
                w.writerow(row)
            rows=e.parse_rows(file)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["id"],"B4_0006862")
            row["candidate_status"]="PHYSICAL_ALLOWED"
            with file.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(row))
                w.writeheader();w.writerow(row)
            with self.assertRaisesRegex(ValueError,"mislabeled"):
                e.parse_rows(file)

    def test_duplicate_legacy_B4_ID_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"data.csv"
            row=self.fixture()
            with file.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(row))
                w.writeheader();w.writerow(row);w.writerow(row)
            with self.assertRaisesRegex(ValueError,"Duplicate"):
                e.parse_rows(file)

    def test_nonfinite_scalar_parameters_and_proxy_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"data.csv"
            for k in ("mH2","production_weighted_nonleptonic_cascade_upper_proxy"):
                row=self.fixture()
                row[k]=math.nan
                with file.open("w",newline="") as f:
                    w=csv.DictWriter(f,fieldnames=list(row))
                    w.writeheader();w.writerow(row)
                with self.assertRaisesRegex(ValueError,"Nonfinite"):
                    e.parse_rows(file)

    def test_collier_rank_locks_diversity_and_requires_RGE_vacuum_fields(self):
        rows=[]
        for i in range(5):
            rows.append({
                "id":f"B4_{i:07d}",
                "mH1_GeV":300. if i<2 else 350.+30*i,
                "mH2_GeV":700. if i<2 else 750.+50*i,
                "gamma":1.02,
                "cascade_upper_proxy":.71-.01*i,
                "maximum_unity_ratio_to_8pi_along_run":.48+.02*i,
                "diagnostic_status":
                    "ORIGINAL_RGE_AND_NO_TREE_DEEPER_WITNESS_DIAGNOSTIC"})
        chosen=e.rank_pool(rows,4)
        self.assertEqual(chosen[0]["id"],"B4_0000000")
        self.assertNotIn("B4_0000001",[x["id"] for x in chosen])
        self.assertTrue(all("NOT_ALLOWED" in e.STATUS for _ in chosen))

    def test_live_C3_C4_C5_dictionary_contracts(self):
        """Verify real backend return dictionaries, not invented mocks."""
        from zee_gateC3_running_complex_bfb import quartic_bfb
        from zee_gateC4_running_55channel_unitarity import (
            scattering_limit,full_trajectory)
        from zee_gateC5_charge_breaking_vacuum_search import evaluate_multistart
        def literal_keys(fn):
            node=ast.parse(textwrap.dedent(inspect.getsource(fn)))
            results=[x.value for x in ast.walk(node)
                     if isinstance(x,ast.Return) and isinstance(x.value,ast.Dict)]
            self.assertTrue(results,"Backend source missing dictionary result")
            return {k.value for z in results for k in z.keys
                    if isinstance(k,ast.Constant) and isinstance(k.value,str)}
        self.assertTrue({
            "ratio_to_8pi","passes_strict_8pi"}<=literal_keys(scattering_limit))
        self.assertTrue({"verdict"}<=literal_keys(quartic_bfb))
        self.assertTrue({
            "status","reached_end_scale","BFB_sufficient_at_all_sampled_steps",
            "tree_unitarity_8pi_at_all_sampled_steps","BFB_negative_witness",
            "first_BFB_uncertified_scale_GeV",
            "first_tree_unitarity_uncertified_scale_GeV",
            "maximum_scattering_eigenvalue_encountered"
        }<=literal_keys(full_trajectory))
        self.assertTrue({
            "status","most_negative_witness","successful_field_evaluations",
            "lowest_point_found"}<=literal_keys(evaluate_multistart))

    def test_two_original_points_full_funnel_synthetic_evidence(self):
        """Exercise the complete E1 data-writing path with mock physics.

        Real 5,557-point numerical validation still MUST run on AF.
        """
        points=[]
        for i in range(2):
            p={"id":f"B4_SYNTH_{i}",
               "mH1":300.+i*45.,"mH2":680.+i*45.,
               "beta":1.2,"gamma":1.1,
               "production_weighted_nonleptonic_cascade_upper_proxy":.70-.1*i}
            points.append(p)

        def fake_run(mod,state,mu0,upper,steps,orbits):
            passed=(state["id"]=="B4_SYNTH_0")
            return {
                "status":"COMPLETE_TO_10TEV" if passed else "STOPPED_SAMPLE",
                "reached_end_scale":passed,
                "BFB_sufficient_at_all_sampled_steps":True,
                "tree_unitarity_8pi_at_all_sampled_steps":passed,
                "BFB_negative_witness":False,
                "first_BFB_uncertified_scale_GeV":None,
                "first_tree_unitarity_uncertified_scale_GeV":None if passed else 800.,
                "maximum_scattering_eigenvalue_encountered":9.0 if passed else 30.}
        mock_solution={
            "status":"NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED",
            "partial_LFV_score_NOT_EXCLUSION":.002,
            "f":{"real":[[0.]*3]*3,"imag":[[0.]*3]*3},
            "Y":{"real":[[0.]*3]*3,"imag":[[0.]*3]*3}}
        mock_vac={
            "status":"NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE",
            "most_negative_witness":None,
            "successful_field_evaluations":128,
            "lowest_point_found":{"difference_from_EW_over_v4":0.}}
        patches=[
            patch("zee_section8_Q4_generated_source_limit_probe.load_generated",
                  return_value=object()),
            patch("zee_gateC1_joined_uv_pilot.scalar_lagrangian",
                  return_value=({"l1":.1},{})),
            patch("zee_gateC1_joined_uv_pilot.build_model_state",
                  side_effect=lambda p,sol:({"id":p["id"]},{})),
            patch("zee_gateC3_running_complex_bfb.quartic_bfb",
                  return_value={"verdict":"BFB_SUFFICIENT_CERTIFIED"}),
            patch("zee_gateC4_running_55channel_unitarity.scattering_limit",
                  return_value={"passes_strict_8pi":True,"ratio_to_8pi":.4}),
            patch("zee_gateC4_running_55channel_unitarity.full_trajectory",
                  side_effect=fake_run),
            patch("zee_gateC5_charge_breaking_vacuum_search.candidate_starts",
                  return_value=np.zeros((128,6))),
            patch("zee_gateC5_charge_breaking_vacuum_search.evaluate_multistart",
                  return_value=mock_vac),
            patch("gateA1b_hierarchical_no_seed.target_neutrino_matrix",
                  return_value=(np.eye(3),np.ones(3))),
            patch("gateA1b_hierarchical_no_seed.antisymmetric_f_with_null_condition",
                  return_value=(np.zeros((3,3)),None)),
            patch("gateB2_zee_neutrino_family_scan.solve_point",
                  return_value=mock_solution),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for obj in patches:
                obj.start()
                self.addCleanup(obj.stop)
            counts,npass,short=e.run(
                points,Path("/mock/pinned-Q4-source"),24,np.zeros((300,5)),
                np.zeros((128,6)),500,20261020,Path(tmp),150)
            self.assertEqual(npass,1)
            self.assertEqual(counts["RGE_two_resolution_pass"],1)
            self.assertEqual(counts["RGE_coarse_not_pass"],1)
            self.assertEqual(counts["original_vacuum_cases_tested"],1)
            self.assertEqual(len(short),1)
            self.assertEqual(short[0]["candidate_id"],"B4_SYNTH_0")
            with (Path(tmp)/"E1_all_5557_original_model_scalar_RGE_diagnostics.jsonl").open() as f:
                ledger=[json.loads(line) for line in f]
            self.assertEqual(len(ledger),2)
            self.assertTrue(all(z["full_Zee_experimental_allowed_or_excluded"] is None
                                for z in ledger))
            self.assertTrue((Path(tmp)/
                "E1_source_exact_neutrino_solutions_for_100_ranked_NOT_ALLOWED.json"
                ).exists())

    def test_unimplemented_observables_are_explicitly_unavailable(self):
        self.assertIn("HiggsTools"," ".join(e.EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED))
        self.assertIn("B_to_Xs_gamma"," ".join(e.EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED))
        self.assertTrue("NOT_ALLOWED" in e.STATUS)
        self.assertTrue("NOT_ALLOWED" in e.BLOCKED)


if __name__=="__main__":
    unittest.main()
