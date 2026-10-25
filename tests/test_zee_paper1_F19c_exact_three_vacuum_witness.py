#!/usr/bin/env python3
"""F19c source-pin + risk-gate tests. Numerical C5 dynamics tested separately.
Synthetic input only: NEVER physics evidence of global vacuum stability.
"""
from __future__ import annotations
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_paper1_F19c_exact_three_vacuum_witness as m

def files(root):
    b=[]
    for n in m.CASES:
        b.append({
            "candidate_id":n,
            "cascade_BR_product_model_LO_2plus3":.44634835330614})
    f18=root/"f18.json"
    f18.write_text(json.dumps({
      "status":"F18_THREE_CASES_CONDOR_OR_LOCAL_MERGED_TREE_LO_NOT_ALLOWED",
      "three_original_benchmarks_LO_MadWidth_completed":True,
      "physical_Zee_model_allowed_or_excluded":None,"benchmarks":b}))
    p={"beta":1.394,"alpha":1.398,"gamma":1.089,"mH1":300.,
       "mH2":700.,"mh2":580.7,"ma":633.7,"m12sq":57700.,
       "lc":4.473,"k1":1.082,"k2":.00398,"k12":-.001266}
    f19=root/"f19.json"
    f19.write_text(json.dumps({
      "status":m.F19_STATUS,
      "F18_merged_JSON_SHA256":m.sha(f18.read_bytes()),
      "F16_original_source_bundle_SHA256":"pinned-source",
      "observational_allowance_or_exclusion":None,
      "benchmarks":[{
         "candidate_id":n,"scalar_original_F16_inputs":p,
         "constraint_gates":{
            "Zee_tree_BFB_sufficient_not_necessary":"SCREEN_PASS",
            "Zee_scalar_2to2_tree_unitarity_8pi":"SCREEN_PASS"}} for n in m.CASES]
    }))
    f19b=root/"f19b.json"
    f19b.write_text(json.dumps({
      "status":m.F19B_STATUS,
      "F19_real_scalar_EWPO_ledger_sha256":m.sha(f19.read_bytes()),
      "F18_exact_merged_sha256":m.sha(f18.read_bytes()),
      "F16_F17f_source_bundle_sha256":"pinned-source",
      "FULL_MODEL_EXPERIMENTALLY_ALLOWED_OR_EXCLUDED":None,
      "results":[{
        "candidate_id":n,
        "physical_Zee_allowed_or_excluded":None,
        "F18_actual_model_tree_cascade_BR":.44634835330614,
        "neutrino_source_fixed_NO_matrix_closure_max_abs_eV":1e-14}
          for n in m.CASES]
    }))
    return f18,f19,f19b

class TestF19cSourceAndVacuums(unittest.TestCase):
    def test_three_actual_benchmarks_join_by_sha(self):
        with tempfile.TemporaryDirectory() as d:
            a,b,c=files(Path(d))
            aa,bb,cc=m.check_inputs(a,b,c)
            self.assertEqual(set(aa),set(m.CASES))
            self.assertEqual(set(bb),set(m.CASES))
            self.assertEqual(set(cc),set(m.CASES))
    def test_source_tamper_fails(self):
        with tempfile.TemporaryDirectory() as d:
            a,b,c=files(Path(d))
            obj=json.loads(b.read_text())
            obj["F18_merged_JSON_SHA256"]="f"*64
            b.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"scalar/EWPO source mismatch"):
                m.check_inputs(a,b,c)
    def test_broken_f19b_prior_source_fails(self):
        with tempfile.TemporaryDirectory() as d:
            a,b,c=files(Path(d))
            obj=json.loads(c.read_text())
            obj["F19_real_scalar_EWPO_ledger_sha256"]="f"*64
            c.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"exact-complex F19b source"):
                m.check_inputs(a,b,c)
    def test_fake_negative_witness_is_explicit_and_no_global_proof(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);a,b,c=files(folder)
            fake_model={"m1":1.,"m2":2.,"m12":3.,"mchi":4.,"muZee":5.}
            def search(point,state,starts,maxiter=650):
                return {
                    # Match the real C5 evaluate_multistart() result contract.
                    "status":"EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS",
                    "search_is_not_a_global_minimization_certificate":True,
                    "starts_requested":len(starts)+2,
                    "most_negative_witness":{
                       "kind":"CHARGE_BREAKING",
                       "difference_from_EW_over_v4":-0.02,
                       "gauge_fixed_fields_over_v":[1.,2.,3.,4.,5.,6.]},
                    "lowest_point_found":{"difference_from_EW_over_v4":-0.02},
                    "successful_field_evaluations":len(starts)+2,
                    "optimizer_failures":0,"boundary_hits":0,
                    "ew":{
                      "stationarity_max_gradient_over_v3":1e-15,
                      "physical_plus_goldstone_spectrum_relmax":1e-14}}
            with patch.object(m,"scalar_lagrangian",return_value=(fake_model,{})),patch.object(
                 m,"evaluate_multistart",side_effect=search):
                got=m.run(a,b,c,folder/"result",multistart=64,maxiter=250)
            self.assertFalse(got["absence_of_witness_proves_global_tree_vacuum"])
            self.assertIsNone(got["full_Zee_theory_and_experimental_allowed"])
            for item in got["cases"]:
                self.assertTrue(item["found_deeper_tree_potential_witness"])
                self.assertFalse(item["EW_tree_global_minimum_certified"])
                self.assertIsNone(item["Zee_model_allowed_or_excluded"])
    def test_bad_marginal_witness_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);a,b,c=files(folder)
            bogus={"status":"EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS",
                   "search_is_not_a_global_minimization_certificate":True,
                   "starts_requested":66,
                   "most_negative_witness":{
                       "kind":"CHARGE_BREAKING",
                       "difference_from_EW_over_v4":-1e-12}}
            with patch.object(m,"scalar_lagrangian",return_value=(
                 {"m1":1.,"m2":2.,"m12":3.,"mchi":4.,"muZee":5.},{})),patch.object(
                 m,"evaluate_multistart",return_value=bogus):
                with self.assertRaisesRegex(ValueError,"value margin"):
                    m.run(a,b,c,folder/"result",multistart=64)
            self.assertFalse((folder/"result").exists())
if __name__=="__main__":unittest.main()
