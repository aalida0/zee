#!/usr/bin/env python3
"""F19 source-safe three-case physics intake integration regressions.

Synthetic only: tests source joins, mathematical ledger semantics, exact
original cohort and explicit NOT_EVALUATED. Real Gate6/GateA1H are called
by the LXPLUS F19 production driver; fake backends are NOT evidence of
real numerical scalar/EWPO screening.
"""
from __future__ import annotations
import hashlib,io,json,math,sys,tarfile,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_paper1_F19_integrated_scalar_EWPO_constraints as m

def digest(b):return hashlib.sha256(b).hexdigest()

def fixture(root):
    bundle=root/"source.tar.gz"
    f16={}
    f17={"CKM_numerical_3_of_3":True,
         "full_complex_lepton_physical_widths_validated":True,
         "CKM_candidate_cards":[]}
    names={}
    for i,n in enumerate(m.CASES):
        scalar=dict(mH1=300.,mH2=700.,mh2=580.7,ma=633.7,
                    beta=1.394,alpha=1.398,gamma=1.089,
                    m12sq=57700.,lc=4.473,k1=1.082,k2=.00398,
                    k12=-.001266)
        f16[n]={"scalar":scalar,"complex_Y_and_f_reconstructed_from_exact_F13":True}
        card=(b"BLOCK MASS\n 25 125\n 35 580.7\n 36 633.7\n"
              b" 37 300\n 9000037 700\n")
        path="original_"+str(i)+".slha"
        f17["CKM_candidate_cards"].append({
            "candidate_id":n,"file":path,"sha256":digest(card)})
        names[m.F17F_SUBDIR+"/"+path]=card
    raw16=json.dumps(f16).encode()
    raw17=json.dumps(f17).encode()
    names[m.F16_FILE]=raw16
    names[m.F17F_FILE]=raw17
    with tarfile.open(bundle,"w:gz") as t:
        for path,data in names.items():
            entry=tarfile.TarInfo(path)
            entry.size=len(data)
            t.addfile(entry,io.BytesIO(data))
    cases=[]
    for row in f17["CKM_candidate_cards"]:
        cases.append({
            "candidate_id":row["candidate_id"],
            "provenance":{"source_F17f_card_SHA256":row["sha256"]},
            "charged_H_decay_tables":{
                "37":{"total_GeV":0.3353617},
                "9000037":{"total_GeV":13.07809}},
            "BR_H2_H1_Z_model_LO_2plus3":0.4502034,
            "BR_H1_tb_model_LO_2plus3":0.9914371,
            "cascade_BR_product_model_LO_2plus3":0.4502034*0.9914371,
            "H2_doublet_weight_sin2gamma":math.sin(1.089)**2,
        })
    merged=root/"merged.json"
    merged.write_text(json.dumps({
        "status":m.F18_MERGE_STATUS,
        "three_original_benchmarks_LO_MadWidth_completed":True,
        "QCD_NLO_or_loop_corrected":False,
        "physical_Zee_model_allowed_or_excluded":None,
        "software_and_flavor_source_provenance":{
            "original_F17f_report_SHA256":digest(raw17)},
        "benchmarks":cases,
    }))
    return merged,bundle

def scalar_backend(**kwargs):
    return {
       "rebuilt_charged_masses_GeV":[kwargs["mH1"],kwargs["mH2"]],
       "rebuilt_neutral_masses_GeV":[125.,kwargs["mh2"]],
       "sufficient_global_quartic_BFB":True,
       "tree_unitarity_pass":True,
       "max_abs_unitarity_eigenvalue":5.0,
    }
def stu_backend(**kwargs):
    return {
        "scalar_STU":{"S":0.03,"T":0.05,"U":-0.03},
        "correlated_fit_screens":{
            "Gfitter_2026_U_floating":{
                "inside_95percent_3D_gaussian_ellipsoid":True,
                "chi2_relative_to_fit_minimum":0.5},
            "PDG_2025_U_floating":{
                "inside_95percent_3D_gaussian_ellipsoid":False,
                "chi2_relative_to_fit_minimum":8.5},
        },
    }

class TestF19IntegratedScalarEWPO(unittest.TestCase):
    def test_exact_three_join_and_no_allowed_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);merged,bundle=fixture(root)
            with patch.object(m,"benchmark",side_effect=scalar_backend),patch.object(
                m,"compute_stu",side_effect=stu_backend):
                result=m.run(merged,bundle,root/"f19_output",quadrature=96)
            self.assertEqual(result["status"],m.F19_STATUS)
            self.assertIsNone(result["observational_allowance_or_exclusion"])
            self.assertEqual(len(result["benchmarks"]),3)
            self.assertTrue((root/"f19_output"/
                "F19_three_scalar_EWPO_vs_cascade_NOT_ALLOWED.csv").is_file())
            for case in result["benchmarks"]:
                self.assertEqual(case["constraint_gates"][
                   "Zee_tree_BFB_sufficient_not_necessary"],"SCREEN_PASS")
                self.assertEqual(case["constraint_gates"][
                   "scalar_STU_PDG_2025_3D_Gaussian_robustness"],
                   "SCREEN_OUTSIDE_95PCT_REGION")
                self.assertEqual(case["constraint_gates"][
                   "general_Zee_complete_LFV_BarrZee_conversion_EDMs"],
                   "NOT_EVALUATED")
                self.assertTrue(case["has_any_screen_red_flag"])
                self.assertIsNone(case["physical_Zee_fully_allowed_or_excluded"])
            with self.assertRaises(FileExistsError):
                m.run(merged,bundle,root/"f19_output")

    def test_input_source_hash_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);merged,bundle=fixture(root)
            data=json.loads(merged.read_text())
            data["software_and_flavor_source_provenance"][
               "original_F17f_report_SHA256"]="f"*64
            merged.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"original F16 source bundle"):
                m.run(merged,bundle,root/"should_not_exist")
            self.assertFalse((root/"should_not_exist").exists())

    def test_missing_original_f18_benchmark_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);merged,bundle=fixture(root)
            data=json.loads(merged.read_text())
            data["benchmarks"].pop()
            merged.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"cohort mismatch"):
                m.run(merged,bundle,root/"should_not_exist")
            self.assertFalse((root/"should_not_exist").exists())

    def test_unity_screen_fail_and_sufficient_BFB_not_certified(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);merged,bundle=fixture(root)
            def bad_scalar(**kwargs):
                x=scalar_backend(**kwargs)
                x["sufficient_global_quartic_BFB"]=False
                x["tree_unitarity_pass"]=False
                return x
            with patch.object(m,"benchmark",side_effect=bad_scalar),patch.object(
                m,"compute_stu",side_effect=stu_backend):
                result=m.run(merged,bundle,root/"f19_output")
            c=result["benchmarks"][0]["constraint_gates"]
            self.assertEqual(c["Zee_tree_BFB_sufficient_not_necessary"],
                             "NOT_CERTIFIED_BY_SUFFICIENT_TEST")
            self.assertEqual(c["Zee_scalar_2to2_tree_unitarity_8pi"],"SCREEN_FAIL")
            self.assertIsNone(result["benchmarks"][0][
                              "physical_Zee_fully_allowed_or_excluded"])

if __name__=="__main__":unittest.main()
