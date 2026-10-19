"""Large one-command Zee scan workflow contracts (synthetic data only).

Fixtures assert provenance/completeness and that no unvalidated
observable can become a physical 'allowed' label. No scanner/RGE is
represented as physically tested by these tests.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_large_integrated_campaign as w


class LargeZeeCampaignContract(unittest.TestCase):
    def test_c1_requires_historical_90_source_rows(self):
        good={"status":"GATE_C1_JOINT_ZEE_MODEL_ONE_LOOP_UV_DIAGNOSTIC_NOT_ALLOWED",
              "row_count":90}
        self.assertEqual(w.expect_stage("C1",good,30,5,8)["validated_cohort_count"],90)
        with self.assertRaises(ValueError):
            w.expect_stage("C1",{**good,"row_count":30},30,5,8)

    def test_240_paired_60_running_and_150_flavor_contracts(self):
        expected=(
          ("C2","GATE_C2_PAIRED_ZEE_SCALAR_RESCUE_ONE_LOOP_DIAGNOSTIC_NOT_ALLOWED",
           "tested_interventions",240),
          ("C3","GATE_C3_COMPLEX_QUARTIC_RUNNING_BFB_DIAGNOSTIC_NOT_ALLOWED",
           "tested",60),
          ("C4","GATE_C4_FULL_COMPLEX_55CHANNEL_RUNNING_SCALAR_UNITARITY_NOT_ALLOWED",
           "tested",60),
          ("C5","GATE_C5_NUMERICAL_FULL_ZEE_CHARGE_BREAKING_VACUUM_NOT_ALLOWED",
           "tested",60),
          ("D1","GATE_D1_AVAILABLE_B2_JOINT_ZEE_NEUTRINO_LFV_PARTIAL_DIAGNOSTIC_NOT_ALLOWED",
           "B2_total_saved_solutions",150),
        )
        for stage,status,key,n in expected:
            with self.subTest(stage=stage):
                obj={"status":status,key:n,"physical_Zee_allowed":None}
                self.assertEqual(w.expect_stage(stage,obj,30,5,8)[
                                 "validated_cohort_count"],n)
                with self.assertRaises(ValueError):
                    w.expect_stage(stage,{**obj,key:n-1},30,5,8)

    def test_invalid_physical_pass_is_rejected(self):
        obj={"status":"GATE_C3_COMPLEX_QUARTIC_RUNNING_BFB_DIAGNOSTIC_NOT_ALLOWED",
             "tested":60,"physical_Zee_allowed":True}
        with self.assertRaises(ValueError):
            w.expect_stage("C3",obj,30,5,8)

    def test_d2_population_not_hardcoded_27(self):
        for n in (1,22,30):
            obj={"status":"GATE_D2_NEUTRINO_EXACT_PARTIAL_LFV_OPTIMIZATION_NOT_ALLOWED",
                 "tested_spectra":n}
            self.assertEqual(w.expect_stage("D2",obj,30,5,8)[
                             "validated_cohort_count"],n)
        with self.assertRaises(ValueError):
            w.expect_stage("D2",{
                "status":"GATE_D2_NEUTRINO_EXACT_PARTIAL_LFV_OPTIMIZATION_NOT_ALLOWED",
                "tested_spectra":0},30,5,8)

    def test_pipeline_must_run_all_diagnostic_components(self):
        stages={k:{"status":"DIAGNOSTIC_COMPLETE_NOT_EXCLUSION"} for k in (
            "neutrino_and_partial_LFV",
            "general_Zee_leptonic_widths",
            "extended_partial_LFV_3lepton_universality",
            "barr_zee_fermion_loop_kernels_NO_amplitudes",
            "barr_zee_fermion_photon_amplitudes_PRELIMINARY",
            "SuperIso_legacy_two_charged","joint_provenance_audit")}
        p={"status":"PARTIAL_DIAGNOSTICS_COMPLETE_NOT_ALLOWED",
           "input_candidate_count":30,
           "full_model_allowed_points":None,"stages":stages}
        w.expect_stage("PIPELINE",p,30,5,8)
        p["stages"]["SuperIso_legacy_two_charged"]["status"]="NOT_RUN"
        with self.assertRaises(ValueError):
            w.expect_stage("PIPELINE",p,30,5,8)

    def test_30_cand_60_case_join_with_only_provisional_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            b4=base/"source.csv"
            joined=base/"B4C_joint_audit"
            joined.mkdir()
            pdir=base/"pipeline"
            (pdir/"B4C_joint_audit").mkdir(parents=True)
            rows=[{"id":f"B4_{i:05d}"} for i in range(30)]
            with b4.open("w",newline="") as h:
                v=csv.DictWriter(h,fieldnames=["id"])
                v.writeheader();v.writerows(rows)
            merged=[]
            for i in range(30):
                merged.append({
                  "candidate_id":f"B4_{i:05d}",
                  "mH1":"300","mH2":"700","gamma":"1.1","tanbeta":"5.6",
                  "b4_nonleptonic_cascade_proxy":"0.6",
                  "B3_cascade_proxy_median":"0.5",
                  "B3_BR_H2_H1Z_median":"0.7",
                  "B3_BR_H1_tb_median":"0.9",
                  "n_B2_flavour_solutions":"5",
                  "min_partial_LFV_score_NOT_EXCLUSION":"1e-7",
                  "legacy_SuperIso_full_Zee_BR":"0.00038"})
            target=pdir/"B4C_joint_audit"/"joint_scalar_neutrino_width_flavour_NOT_ALLOWED.csv"
            with target.open("w",newline="") as f:
                wr=csv.DictWriter(f,fieldnames=list(merged[0]))
                wr.writeheader();wr.writerows(merged)
            c4,c5=[],[]
            for i in range(30):
                for label in ("vA","vB"):
                    key=f"B4_{i:05d}"
                    c4.append({"candidate_id":key,"variant":label,
                               "both_running_theory_screens_pass":True})
                    c5.append({"candidate_id":key,"variant":label,
                               "C5_deeper_witness":i==0 and label=="vB"})
            result=w.synthesize(base,b4,pdir,{"cases":c4},
                {"rows":c5},{},None,5)
            self.assertEqual(result["number_scalar_candidates"],30)
            self.assertEqual(result["number_paired_running_and_vacuum_cases"],60)
            self.assertEqual(result[
                "number_diagnostic_candidates_for_further_constraints"],30)
            self.assertIsNone(result["number_physically_allowed_Zee_points"])
            saved=w.csv_rows(base/"joined_30_scalar_campaign_prioritization_NOT_ALLOWED.csv")
            self.assertEqual(len(saved),30)
            self.assertTrue(all(z["full_Zee_experimental_allowed"]=="" for z in saved))

if __name__=="__main__":
    unittest.main()
