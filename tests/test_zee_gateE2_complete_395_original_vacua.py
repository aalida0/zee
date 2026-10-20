"""E2: 395-case original-potential audit and safe resumable C5 funnel tests.

All fixtures are SYNTHETIC. No result is a numerical-vacuum physics test.
"""
import csv
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateE2_complete_395_original_vacua as m


class E2Contracts(unittest.TestCase):
    def base_case(self, name="B4_SYNTH_01", witness=False):
        return {
            "candidate_id":name,
            "mH1_GeV":300.,
            "mH2_GeV":700.,
            "gamma":1.1,
            "cascade_upper_proxy":0.65,
            "maximum_unity_ratio_to_8pi_along_run":0.7,
            "original_tree_vacuum_status":
                "EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS"
                if witness else
                "NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE",
            "C5_explicit_deeper_original_tree_potential_witness":witness,
            "global_vacuum_proven":False,
            "full_Zee_experimental_allowed_or_excluded":None,
        }

    def test_C5_status_and_footprint_fail_closed(self):
        yes=self.base_case(witness=True)
        no=self.base_case()
        self.assertTrue(m.validate_vacuum_record(yes,"B4_SYNTH_01"))
        self.assertTrue(m.validate_vacuum_record(no,"B4_SYNTH_01"))
        for bad in (
            {**no,"original_tree_vacuum_status":"ALLOWED"},
            {**yes,"C5_explicit_deeper_original_tree_potential_witness":False},
            {**no,"global_vacuum_proven":True},
            {**no,"full_Zee_experimental_allowed_or_excluded":True},
            {**no,"cascade_upper_proxy":float("nan")},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    m.validate_vacuum_record(bad,"B4_SYNTH_01")

    def test_checkpoint_cannot_repeat_or_import_old_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            progress=Path(tmp)/"checkpoint.jsonl"
            good=self.base_case("B4_UNTESTED")
            data={"remaining":["B4_UNTESTED"]}
            progress.write_text(json.dumps(good)+"\n")
            self.assertEqual(len(m.read_checkpoint(progress,data)),1)
            progress.write_text(json.dumps(good)+"\n"+json.dumps(good)+"\n")
            with self.assertRaisesRegex(ValueError,"Duplicate"):
                m.read_checkpoint(progress,data)
            progress.write_text(json.dumps(self.base_case("B4_OLD"))+"\n")
            with self.assertRaisesRegex(ValueError,"out-of-cohort"):
                m.read_checkpoint(progress,data)

    def test_exact_B2_reference_compares_both_complex_arrays(self):
        arr={"real":[[0.,1.,0.],[0.,0.,0.],[0.,0.,0.]],
             "imag":[[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]]}
        other={"real":[[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]],
               "imag":[[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]]}
        saved={"f":arr,"Y":other,"partial_LFV_score_NOT_EXCLUSION":1e-5,
               "neutrino_matrix_closure_eV":1e-17}
        m.assert_reproduced(saved,saved,"fixture")
        altered={**saved,"Y":arr}
        with self.assertRaisesRegex(ValueError,"texture drift"):
            m.assert_reproduced(saved,altered,"fixture")
        altered={**saved,"partial_LFV_score_NOT_EXCLUSION":2e-5}
        with self.assertRaisesRegex(ValueError,"scoring drift"):
            m.assert_reproduced(saved,altered,"fixture")

    def make_campaign_fixture(self,root):
        campaign=root/"campaign"
        e1=root/"e1"
        (campaign/"B4_adaptive").mkdir(parents=True)
        e1.mkdir()
        original=campaign/"B4_adaptive"/"all_screened_candidates_NOT_ALLOWED.csv"
        points={}
        for i in range(5557):
            name=f"B4_SYNTH_{i:05d}"
            points[name]={
                "id":name,"mH1":300.+(i%37)*3.,
                "mH2":700.+(i%73)*4.,"gamma":1.1,
                "cascade_upper_proxy":.70-(i%70)*.001}
        with original.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=["id","mH1","mH2","gamma"])
            writer.writeheader()
            writer.writerows({k:x[k] for k in ("id","mH1","mH2","gamma")}
                             for x in points.values())
        ids=list(points)[:395]
        ledger=e1/"E1_all_5557_original_model_scalar_RGE_diagnostics.jsonl"
        with ledger.open("w") as f:
            for i,(name,point) in enumerate(points.items()):
                row={
                    "candidate_id":name,
                    "gamma":1.1,
                    "mH1_GeV":point["mH1"],
                    "mH2_GeV":point["mH2"],
                    "cascade_upper_proxy":point["cascade_upper_proxy"],
                    "maximum_unity_ratio_to_8pi_along_run":.6,
                    "original_1loop_RGE_10TeV_screen":
                        True if i<395 else None,
                    "diagnostic_status":"RGE_PASS_VACUUM_NOT_YET_TESTED"
                        if i<395 else "ORIGINAL_RGE_COARSE_NOT_10TEV_CERTIFIED",
                    "full_Zee_experimental_allowed_or_excluded":None}
                f.write(json.dumps(row)+"\n")
        tested=e1/"E1_vacuum_tested_original_models.json"
        old=[]
        for i,name in enumerate(ids[:150]):
            item=self.base_case(name,witness=i<44)
            item["cascade_upper_proxy"]=points[name]["cascade_upper_proxy"]
            old.append(item)
        tested.write_text(json.dumps(old)+"\n")
        saved40=e1/"E1_source_exact_neutrino_solutions_for_100_ranked_NOT_ALLOWED.json"
        saved40.write_text(json.dumps({ids[i]:{} for i in range(44,84)})+"\n")
        provenance={"known":"fixture"}
        e1summary=e1/"summary.json"
        e1summary.write_text(json.dumps({
            "status":m.E1_STATUS,
            "input_original_B4_scalar_EWPO_points":5557,
            "RGE_two_resolution_pass_all_before_vacuum":395,
            "RGE_screens_passing_but_vacuum_not_evaluated":245,
            "vacuum_followup_limit":150,
            "original_B4_10TeV_plus_numerical_vacuum_no_witness_tested":106,
            "source_provenance":provenance,
            "output_file_SHA256":{
                p.name:m.digest(p) for p in (ledger,tested,saved40)}})+"\n")
        return campaign,e1,points,provenance

    def test_full_E1_5557_395_150_245_partition(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            campaign,e1,points,prov=self.make_campaign_fixture(root)
            dummy=root/"RGEs.py"
            dummy.write_text("source fixture")
            post=root/"postscan.json"
            post.write_text("{}")
            with patch.object(m,"verify_prior",return_value=(
                    list(points.values()),dummy,prov)):
                data=m.load_e1(campaign,e1,post,root/"generator",root/"q4.json")
            self.assertEqual(len(data["rge_pass"]),395)
            self.assertEqual(len(data["old"]),150)
            self.assertEqual(len(data["remaining"]),245)
            self.assertEqual(set(data["old"])&set(data["remaining"]),set())
            self.assertEqual(set(data["old"])|set(data["remaining"]),
                             set(data["rge_pass"]))
            with patch.object(m,"verify_prior",return_value=(
                    list(points.values()),dummy,prov)):
                led=e1/"E1_all_5557_original_model_scalar_RGE_diagnostics.jsonl"
                with led.open("a") as f:f.write("\n")
                with self.assertRaises((ValueError,json.JSONDecodeError)):
                    m.load_e1(campaign,e1,post,root/"generator",root/"q4.json")

    def test_finalize_keeps_all_survivors_not_just_diverse_rank(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            campaign,e1,points,prov=self.make_campaign_fixture(root)
            dummy=root/"RGEs.py"
            dummy.write_text("source fixture")
            post=root/"postscan.json"
            post.write_text("{}")
            with patch.object(m,"verify_prior",return_value=(
                    list(points.values()),dummy,prov)):
                data=m.load_e1(campaign,e1,post,root/"generator",root/"q4.json")
            new={name:{
                 **self.base_case(name),
                 "cascade_upper_proxy":data["rge_pass"][name]["cascade_upper_proxy"]}
                 for name in data["remaining"]}
            no_reproduction={"status":"NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED",
                             "partial_LFV_score_NOT_EXCLUSION":1e-5,
                             "neutrino_matrix_closure_eV":0.,
                             "f":{"real":[[0.]*3]*3,"imag":[[0.]*3]*3},
                             "Y":{"real":[[0.]*3]*3,"imag":[[0.]*3]*3}}
            out=root/"out"
            out.mkdir()
            with patch.object(m,"reproduce_single_B2",
                              return_value=no_reproduction):
                # Saved source 40 are empty fixture objects. Supply an
                # independent saved-result row for this data-only test.
                data["saved40"]={}
                for item in data["rge_pass"].values():
                    item["single_B2_partial_LFV_score_NOT_EXCLUSION"]=1e-5
                summary=m.finalize(data,out,new,{
                    "seed":20261020,"vacuum_multistarts":128,
                    "vacuum_maxiter":1000})
            self.assertEqual(
                summary["all_RGE_qualified_original_potentials_vacuum_evaluated"],395)
            self.assertEqual(summary["explicit_deeper_tree_vacuum_witnesses"],44)
            self.assertEqual(summary["no_deeper_tree_vacuum_witness_found"],351)
            self.assertIsNone(summary["full_Zee_experimental_allowed_or_excluded"])
            with (out/"E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv").open() as f:
                self.assertEqual(len(list(csv.DictReader(f))),351)
            with (out/"E2_all_395_original_B4_vacuum_evidence.jsonl").open() as f:
                self.assertEqual(sum(1 for _ in f),395)


if __name__=="__main__":
    unittest.main()
