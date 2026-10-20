"""E4H: 309-point h125 direct LFV source/return and physics-label tests.

Fixtures test code integration, not full model production/acceptance.
"""
import json,math,sys,tempfile,unittest,ast,inspect,textwrap
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateE4h_309_direct_h125_lfv_screen as h


class H125DirectContract(unittest.TestCase):
 def fixture(self):
  m={"real":[[0.]*3 for _ in range(3)],
     "imag":[[0.]*3 for _ in range(3)]}
  p={"id":"B4_TEST","mH1":300.,"mH2":700.,"mh2":580.,
     "ma":620.,"alpha":1.2,"beta":1.3,"gamma":1.1,
     "production_weighted_nonleptonic_cascade_upper_proxy":.55}
  s={"candidate_id":"B4_TEST",
     "selected_D4_extended_partial_LFV_score_NOT_EXCLUSION":.02,
     "D2":{"chosen_optimized_source":{"solution":{
       "candidate_id":"B4_TEST","f":m,"Y":m}}}}
  return p,s

 def mock_widths(self,emu=1e-7,etau=1e-4,mutau=1e-4):
  d={"h_to_e_mu":emu,"h_to_e_tau":etau,"h_to_mu_tau":mutau}
  return {
   "leptonic_updated_BR_proxy":d,"nominal_SM_reference_BR":d,
   "h125_LFV_partial_widths_GeV":{k:v*.004 for k,v in d.items()},
   "h125_leptonic_only_width_updated_GeV":.004,
   "kappa_V_tree":.99,"kappa_top_TypeII_ansatz":1.01,
   "kappa_bottom_TypeII_ansatz":.95}

 def test_exact_tree_width_backend_and_D4_source_closure(self):
  p,s=self.fixture()
  with patch.object(h,"h125_widths",
                    return_value=self.mock_widths()),\
       patch.object(h,"compare_partial",return_value={
         "new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION":.02}):
   result=h.analyze(p,s)
  self.assertTrue(result[
      "all_three_SM_production_direct_reference_screens_below_one_NOT_PASS"])
  self.assertAlmostEqual(result[
      "h125_leptonic_updated_reference_limit_ratios"]["h_to_e_mu"],
      1e-7/4.4e-5)
  self.assertIsNone(result["physical_Zee_allowed_or_excluded"])

 def test_direct_h125_reference_tension_not_exclusion(self):
  p,s=self.fixture()
  with patch.object(h,"h125_widths",
                    return_value=self.mock_widths(emu=.0001)):
   result=h.analyze(p,s,check_d4=False)
  self.assertFalse(result[
      "all_three_SM_production_direct_reference_screens_below_one_NOT_PASS"])
  self.assertGreater(result["worst_h125_direct_reference_ratio"],2.)
  self.assertIsNone(result["physical_Zee_allowed_or_excluded"])

 def test_D4_inconsistent_recomputation_fails_closed(self):
  p,s=self.fixture()
  with patch.object(h,"compare_partial",return_value={
       "new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION":.7}):
   with self.assertRaisesRegex(ValueError,"D4 coherent LFV"):
    h.analyze(p,s)

 def test_complete_309_aggregation_retains_unknown_labels(self):
  with tempfile.TemporaryDirectory() as tmp:
   p,s=self.fixture()
   with patch.object(h,"h125_widths",
                     return_value=self.mock_widths()):
    row=h.analyze(p,s,check_d4=False)
   src={}
   points={}
   for i in range(309):
    k=f"B4_{i:05d}"
    z={**row,"candidate_id":k}
    if i%7==0:
     z["all_three_SM_production_direct_reference_screens_below_one_NOT_PASS"]=False
     z["worst_h125_direct_reference_ratio"]=10.
    src[k]=z
    points[k]={"id":k}
   summary=h.finish(Path(tmp),points,src,{"mock":"source"})
   self.assertEqual(summary["E3_optimized_original_models_tested"],309)
   self.assertEqual(summary["direct_Higgs_reference_tensions_NOT_physical_excluded"],45)
   self.assertIsNone(summary["full_Zee_allowed_or_excluded"])
   self.assertTrue((Path(tmp)/"E4H_309_ranked_direct_h125_LFV_NOT_ALLOWED.csv").exists())

 def test_reject_bad_models_and_incomplete_population(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(ValueError,"incomplete"):
    h.finish(Path(tmp),{}, {},{})
  self.assertEqual(h.LIMITS["h_to_e_mu"][0],4.4e-5)
  self.assertEqual(h.LIMITS["h_to_e_tau"][0],.0020)
  self.assertEqual(h.LIMITS["h_to_mu_tau"][0],.0015)

 def test_live_source_expected_h125_width_fields(self):
  from zee_gateD5_h125_direct_LFV_27 import h125_widths
  from zee_gateD4_W_photon_barr_zee_27 import compare_partial
  def return_dict_keys(fun):
   tree=ast.parse(textwrap.dedent(inspect.getsource(fun)))
   return {k.value for ret in ast.walk(tree)
           if isinstance(ret,ast.Return) and ret.value is not None
           for dic in ast.walk(ret.value) if isinstance(dic,ast.Dict)
           for k in dic.keys if isinstance(k,ast.Constant)
           and isinstance(k.value,str)}
  self.assertTrue({
   "h125_LFV_partial_widths_GeV",
   "leptonic_updated_BR_proxy","nominal_SM_reference_BR",
   "kappa_V_tree","kappa_top_TypeII_ansatz",
   "kappa_bottom_TypeII_ansatz"}<=return_dict_keys(h125_widths))
  self.assertIn("new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION",
                return_dict_keys(compare_partial))

if __name__=="__main__":
 unittest.main()
