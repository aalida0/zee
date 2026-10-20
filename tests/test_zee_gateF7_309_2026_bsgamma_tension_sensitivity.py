"""F7 source-safe tests: sensitivity calculations must never fake 2026 exclusions."""
import csv,json,math,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateF7_309_2026_bsgamma_tension_sensitivity as f
from zee_gateF6_309_full_legacy_bsgamma import STATUS as F6_STATUS

LEGACY_SM=.0003382457724040796
IDS=list(f.PRIORITY)+[f"B4_{i:07d}" for i in range(303)]
assert len(set(IDS))==309

def original(k,i,delta=None):
 shift=float((4.1349849242596696e-05+i*1e-7)
              if delta is None else delta)
 br=LEGACY_SM+shift
 return {
  "candidate_id":k,"mH1_GeV":200.+i*.1,
  "mH2_GeV":700.+i*.2,"gamma":1.089,"tanbeta":5.59717,
  "HiggsSignals_E6_delta_chi2_NOT_CL":i*.05,
  "E7_included_cascade_proxy_NOT_physical_rate":.6-i*.0003,
  "F5_strict_C7eff_projector_not_rate":.02,
  "BR_BtoXsgamma_legacy_SuperIso_two_state":br,
  "BR_BtoXsgamma_legacy_SuperIso_SM_reference":LEGACY_SM,
  "legacy_BR_NP_minus_SM":shift,
  "legacy_BR_ratio_to_same_legacy_SM":br/LEGACY_SM,
  "A1U_source_diagnostics":{"full_legacy_Zee_BR":br},
  "modern_2026_NNLO_and_likelihood_validated":False,
  "full_Zee_allowed_excluded":None,
 }

def make_f6(folder,change=None):
 v={k:original(k,i) for i,k in enumerate(IDS)}
 if change:
  change(v)
 records=folder/f.F6_FILE
 with records.open("w") as h:
  for k in IDS:h.write(json.dumps(v[k])+"\n")
 c=folder/"F6_309_legacy_BR_HS_cascade_NO_CL.csv"
 with c.open("w",newline="") as h:
  w=csv.DictWriter(h,fieldnames=(
      "candidate_id","BR_BtoXsgamma_legacy_SuperIso_two_state"))
  w.writeheader()
  for k in IDS:w.writerow({
      "candidate_id":k,
      "BR_BtoXsgamma_legacy_SuperIso_two_state":
         v[k]["BR_BtoXsgamma_legacy_SuperIso_two_state"]})
 p=folder/"F6_E7_Pareto_legacy_BR_NO_CL.csv"
 with p.open("w",newline="") as h:
  w=csv.DictWriter(h,fieldnames=(
       "candidate_id","BR_BtoXsgamma_legacy_SuperIso_two_state"))
  w.writeheader()
  for k in f.PRIORITY:w.writerow({
       "candidate_id":k,
       "BR_BtoXsgamma_legacy_SuperIso_two_state":
          v[k]["BR_BtoXsgamma_legacy_SuperIso_two_state"]})
 br=sorted(z["BR_BtoXsgamma_legacy_SuperIso_two_state"] for z in v.values())
 ds=sorted(z["legacy_BR_NP_minus_SM"] for z in v.values())
 source={"new_F6_script_SHA256":f.digest(
     f.ROOT/"scripts/zee_gateF6_309_full_legacy_bsgamma.py")}
 summary={
  "status":F6_STATUS,"original_source_points":309,
  "A1U_historical_full_inclusive_kernel_reproduced":True,
  "A1U_SM_TypeII_endpoints_and_equal_masses_validated":True,
  "A1U_source_context_matching_interposition_checked_every_point":True,
  "full_legacy_SuperIso_inclusive_BR_309_computed":True,
  "modern_2026_matching_and_theory_uncertainties_calibrated":False,
  "experimental_95CL_likelihood_validated":False,
  "Zee_allowed_or_excluded":None,"source_provenance":source,
  "legacy_SM_BR":LEGACY_SM,
  "legacy_BR_min_median_max":[br[0],br[154],br[-1]],
  "legacy_NP_minus_SM_min_median_max":[ds[0],ds[154],ds[-1]],
  "legacy_BtoXsGamma_above_same_legacy_SM":sum(z>0 for z in ds),
  "priority_six":{k:{} for k in f.PRIORITY},
  "output_hashes":{x.name:f.digest(x) for x in (records,c,p)},
 }
 f.writejson(folder/"summary.json",summary)
 f.writejson(folder/"manifest.json",{
     "status":F6_STATUS,"source":source,
     "summary_SHA256":f.digest(folder/"summary.json")})
 return v

class F7Sensitivity(unittest.TestCase):
 def test_published_reference_values_exact(self):
  self.assertAlmostEqual(f.REFERENCE["modern_SM_central"],3.54e-4)
  self.assertAlmostEqual(f.REFERENCE["modern_SM_sigma"],.14e-4)
  self.assertAlmostEqual(f.REFERENCE["experimental_central"],3.49e-4)
  self.assertAlmostEqual(f.REFERENCE["experimental_sigma"],.19e-4)
  self.assertEqual(f.REFERENCE["Egamma_min_GeV"],1.6)
  self.assertFalse("EXCLUDED" in f.STATUS)
  self.assertIn("NOT_EXCLUSION",f.STATUS)

 def test_nominal_what_if_never_a_matched_rate_or_CL(self):
  d=4.93828643917e-05
  y=f.gaussian_what_if(d)
  self.assertAlmostEqual(
      y["HYPOTHETICAL_2026SM_PLUS_scaled_legacy_delta_NOT_a_model_BR"],
      4.033828643917e-4,places=13)
  self.assertAlmostEqual(y["Gaussian_what_if_pull_NOT_model_likelihood"],
                         2.30427591739656,places=9)
  self.assertFalse(y[
      "within_illustrative_two_sided_1p96_band_NOT_allowed_or_excluded"])
  self.assertAlmostEqual(f.gaussian_what_if(0)["Gaussian_what_if_pull_NOT_model_likelihood"],
                         .05/math.hypot(.14,.19))

 def test_primary_B4_requires_16point45_percent_shift_change(self):
  z=original("B4_0004143",0,4.93828643917e-05)
  q=f.model_row(z)
  self.assertAlmostEqual(q["illustrative_scale_to_1p96_upper_edge"],
                         .8354651253089659,places=8)
  self.assertAlmostEqual(q["illustrative_NP_shift_suppression_fraction_to_1p96"],
                         .1645348746910341,places=8)
  self.assertGreater(q["illustrative_extra_SM_uncertainty_quadrature_for_1p96"],0.)
  self.assertTrue(q["no_validated_model_BtoXsgamma_2026_rate"])
  self.assertIsNone(q["experimentally_allowed_or_excluded"])

 def test_36_scenarios_change_counter_as_expected(self):
  models=[f.model_row(original(k,i)) for i,k in enumerate(IDS)]
  x=f.scenario_counts(models)
  self.assertEqual(len(x),36)
  find=lambda k,s:next(z for z in x if
    z["hypothetical_NP_shift_scale"]==k and
    z["hypothetical_SM_sigma_inflation"]==s)
  a=find(0.,1.)
  self.assertEqual(a["number_illustratively_beyond_positive_1p96_NOT_exclusion"],0)
  self.assertTrue(all(z["modern_BSM_likelihood_evaluated"] is False for z in x))
  self.assertGreaterEqual(
      find(1.,1.)["number_illustratively_beyond_positive_1p96_NOT_exclusion"],
      find(.8,1.)["number_illustratively_beyond_positive_1p96_NOT_exclusion"])
  self.assertGreaterEqual(
      find(1.,1.)["number_illustratively_beyond_positive_1p96_NOT_exclusion"],
      find(1.,2.)["number_illustratively_beyond_positive_1p96_NOT_exclusion"])

 def test_f6_complete_archived_cohort_and_hash_validation(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)
   make_f6(path)
   v,source=f.load_f6(path)
   self.assertEqual(len(v),309)
   self.assertIn("F6_rows_SHA256",source)
   with (path/f.F6_FILE).open("a") as h:h.write("{}\n")
   with self.assertRaisesRegex(ValueError,"SHA mismatch"):
    f.load_f6(path)

 def test_f6_rejects_tampered_source_or_fabricated_exclusion(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)
   make_f6(path)
   z=f.load(path/"summary.json")
   z["source_provenance"]["new_F6_script_SHA256"]="invalid"
   f.writejson(path/"summary.json",z)
   m=f.load(path/"manifest.json")
   m["source"]=z["source_provenance"]
   m["summary_SHA256"]=f.digest(path/"summary.json")
   f.writejson(path/"manifest.json",m)
   with self.assertRaisesRegex(ValueError,"source-status/manifest"):
    f.load_f6(path)
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)
   make_f6(path,lambda v:v[IDS[0]].update({"full_Zee_allowed_excluded":True}))
   with self.assertRaisesRegex(ValueError,"false physical-CL"):
    f.load_f6(path)

 def test_f6_rejects_Br_minus_SM_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)
   make_f6(path,lambda v:v[IDS[0]].update({
        "legacy_BR_NP_minus_SM":1e-5}))
   with self.assertRaisesRegex(ValueError,"crosscheck failed"):
    f.load_f6(path)

 def test_write_309_complete_priority_six_and_no_exclusions(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)
   models=[f.model_row(original(k,i)) for i,k in enumerate(IDS)]
   z=f.write_outputs(path,models,{"synthetic":True})
   self.assertEqual(z["total_source_models"],309)
   self.assertIsNone(z["all_309_Zee_allowed_or_excluded"])
   self.assertFalse(z["full_experimental_likelihood_evaluated"])
   self.assertFalse(z["2026_model_BSM_matching_derived"])
   self.assertEqual(z["num_sensitivity_scenarios"],36)
   self.assertEqual(len(z["priority_six"]),6)
   with (path/"F7_309_HS_cascade_legacy_vs_modern_Gaussian_DIAGNOSTIC.csv").open() as h:
    self.assertEqual(len(list(csv.DictReader(h))),309)
   models[0]["experimentally_allowed_or_excluded"]=False
   with self.assertRaisesRegex(ValueError,"fabricate"):
    f.write_outputs(path,models,{})

 def test_all_309_and_nonfinite_input_required(self):
  with tempfile.TemporaryDirectory() as d:
   models=[f.model_row(original(k,i)) for i,k in enumerate(IDS)]
   with self.assertRaisesRegex(ValueError,"incomplete 309"):
    f.write_outputs(Path(d),models[:-1],{})
   with self.assertRaisesRegex(ValueError,"incomplete 309"):
    f.write_outputs(Path(d),models[:-1]+[models[0]],{})
  with self.assertRaisesRegex(ValueError,"nonfinite"):
   f.gaussian_what_if(float("nan"))
  with self.assertRaisesRegex(ValueError,"invalid hypothetical"):
   f.gaussian_what_if(0,-1.,1.)

if __name__=="__main__":unittest.main()
