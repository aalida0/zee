#!/usr/bin/env python3
"""F19d analytic Type-II two-charged LO source-join regressions.

Synthetic cohort only. These are code checks, NOT original AF
SuperIso matching nor modern experimental exclusions.
"""
from __future__ import annotations
import json,math,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_paper1_F19d_AF_independent_analytic_LO_bsgamma as m

def fixture(root):
    original=root/"f18.json"
    original.write_text(json.dumps({
       "status":"F18_THREE_CASES_CONDOR_OR_LOCAL_MERGED_TREE_LO_NOT_ALLOWED",
       "three_original_benchmarks_LO_MadWidth_completed":True,
       "physical_Zee_model_allowed_or_excluded":None,
       "benchmarks":[{
         "candidate_id":k,"cascade_BR_product_model_LO_2plus3":.46}
           for k in m.CASES]}))
    scalar=root/"f19.json"
    p=dict(mH1=550.,mH2=880.,beta=1.394,gamma=1.089)
    scalar.write_text(json.dumps({
       "status":"F19_REAL_F18_THREE_SCALAR_BFB_UNITARITY_STU_SCREENS_NOT_FULL_ZEE_ALLOWED",
       "F18_merged_JSON_SHA256":m.sha(original),
       "F16_original_source_bundle_SHA256":"original_bundle",
       "observational_allowance_or_exclusion":None,
       "benchmarks":[{
          "candidate_id":k,"BR_cascade_tree_MadWidth":.46,
          "scalar_original_F16_inputs":p} for k in m.CASES]}))
    flavor=root/"f19b.json"
    flavor.write_text(json.dumps({
       "status":"F19B_EXACT_F17F_COMPLEX_NEUTRINO_PARTIAL_LFV_NOT_FULL_EXCLUSION",
       "F18_exact_merged_sha256":m.sha(original),
       "F19_real_scalar_EWPO_ledger_sha256":m.sha(scalar),
       "F16_F17f_source_bundle_sha256":"original_bundle",
       "FULL_MODEL_EXPERIMENTALLY_ALLOWED_OR_EXCLUDED":None,
       "results":[{
          "candidate_id":k,"F18_actual_model_tree_cascade_BR":.46}
          for k in m.CASES]}))
    vac=root/"f19c.json"
    vac.write_text(json.dumps({
       "status":"F19C_EXACT_F18_F19B_TREE_CHARGE_BREAKING_VACUUM_WITNESS_SCREEN_NOT_GLOBAL",
       "original_F18_SHA256":m.sha(original),
       "original_F19_SHA256":m.sha(scalar),
       "original_F19b_SHA256":m.sha(flavor),
       "full_Zee_theory_and_experimental_allowed":None,
       "cases":[{
          "candidate_id":k,"BR_cascade_tree_MadWidth":.46}
          for k in m.CASES]}))
    return original,scalar,flavor,vac

class TestF19dAnalyticalNoAF(unittest.TestCase):
    def test_0907_1791_f7_f8_formulas_at_y_quarter(self):
        k=m.kernels(.25)
        # Independent reference values evaluated from published closed forms.
        self.assertAlmostEqual(k["F7_1"],-.04405590363457465,places=13)
        self.assertAlmostEqual(k["F8_1"],-.030734168722979183,places=13)
        self.assertAlmostEqual(k["F7_2"],-.10633263717529513,places=13)
        self.assertAlmostEqual(k["F8_2"],-.10519832922070826,places=13)

    def test_typeii_negative_c7c8_and_670_ratio(self):
        ref=m.model(670.,670.001,1.394,0.0001,163.)
        self.assertLess(ref["delta_C7_LO_analytic"],0.)
        self.assertLess(ref["delta_C8_LO_analytic"],0.)
        self.assertGreater(ref["linearized_2026_shift_x1e4"],0.)
        self.assertAlmostEqual(ref["Zee_shift_over_TypeII670_shift_LO_NOT_CL"],
                              1.,delta=1e-4)
        self.assertFalse(ref["A1S_SuperIso_source_reproduced"])
        self.assertIsNone(ref["full_NNLO_flavor_likelihood"])

    def test_mix_weight_and_heavy_decoupling(self):
        b,g=1.394,1.09
        a=m.model(550.,880.,b,g,163.)
        self.assertAlmostEqual(a["weight_H1_cos2gamma"]+
                               a["weight_H2_sin2gamma"],1.,places=13)
        c=m.model(550.,1e7,b,g,163.)
        s=m.single(550.,math.tan(b),163.)
        self.assertAlmostEqual(c["delta_C7_LO_analytic"],
                               math.cos(g)**2*s[0],delta=1e-7)
        self.assertLess(a["delta_C7_LO_analytic"],0.)

    def test_exact_four_stage_sha_join_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            paths=fixture(root)
            _,_,allcohort=m.checked_cohort(*paths)
            self.assertEqual(len(allcohort),4)
            x=m.run(*paths,root/"result")
            self.assertEqual(len(x["rows"]),9)
            self.assertTrue(x["AF_original_F13_csv_unavailable_not_required"])
            self.assertFalse(x["original_SuperIso_A1S_running_mt_and_vendor_revalidated"])
            self.assertIsNone(x["full_B_to_Xs_gamma_95CL"])
            self.assertIsNone(x["full_Zee_model_experimentally_allowed_or_excluded"])
            with self.assertRaises(FileExistsError):
                m.run(*paths,root/"result")

    def test_f19b_hash_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            paths=fixture(Path(temp))
            p=paths[2];d=json.loads(p.read_text())
            d["F18_exact_merged_sha256"]="0"*64
            p.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,"F19b SHA"):
                m.checked_cohort(*paths)

    def test_nonphysical_running_top_or_mixing_rejected(self):
        with self.assertRaises(ValueError):m.kernels(float("nan"))
        with self.assertRaises(ValueError):m.kernels(1.)
        with self.assertRaises(ValueError):m.model(550.,880.,1.394,0.,163.)
        with self.assertRaises(ValueError):m.single(550.,5.7,-163.)

if __name__=="__main__":unittest.main()
