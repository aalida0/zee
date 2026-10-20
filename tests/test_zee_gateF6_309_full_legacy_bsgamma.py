"""F6 source-safe 309-point legacy SuperIso full rate accounting regressions.

No invented modern/2026 branching-ratio likelihood. Actual vendor source
and full C A1U calculation run only on AF with pinned historic A1U/A1R.
"""
from __future__ import annotations
import contextlib,csv,io,json,math,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateF6_309_full_legacy_bsgamma as g

def fake_e7(k):
 return {"candidate_id":k,"mH1_GeV":210.,"mH2_GeV":680.,
  "gamma":1.1,"tanbeta":5.63,
  "charged_cascade_included_channel_proxy_NOT_physical_rate":.6,
  "HS_delta_chi2_E6_vs_fixed_SM":.8}

def fake_f5(k):
 r=fake_e7(k)
 return {"candidate_id":k,"mH1_GeV":r["mH1_GeV"],
   "mH2_GeV":r["mH2_GeV"],"gamma":r["gamma"],
   "tanbeta":r["tanbeta"],
   "E7_included_channel_cascade_proxy_NOT_signal":
    r["charged_cascade_included_channel_proxy_NOT_physical_rate"],
   "E6_HiggsSignals_delta_chi2_NOT_CL":
    r["HS_delta_chi2_E6_vs_fixed_SM"],
   "Q7eff_NP_strictly_truncated_LO_plus_NLO":.0199,
   "model_excluded_allowed":None}

def fake_full_legacy(m1,m2,gam,t):
 sm=.0003382457724
 return {
  "full_legacy_Zee_BR":.000402+(m1-210)*1e-9,
  "full_single_state_BR":{"H1":.000405,"H2":.000380,"SM":sm},
  "high_scale_fixed_RG_context_max_abs_delta_H1":0.,
  "high_scale_fixed_RG_context_max_abs_delta_H2":0.,
  "fixed_low_context_numeric_separation":{"SM_minus_H1":0.,
                                          "SM_minus_H2":0.},
 }

def fake_record(k,br=None):
 legacy=.000402 if br is None else br
 return {
  "candidate_id":k,"mH1_GeV":210.,"mH2_GeV":680.,
  "gamma":1.1,"tanbeta":5.63,
  "HiggsSignals_E6_delta_chi2_NOT_CL":.8,
  "E7_included_cascade_proxy_NOT_physical_rate":.6,
  "F5_strict_C7eff_projector_not_rate":.0199,
  "BR_BtoXsgamma_legacy_SuperIso_two_state":legacy,
  "BR_BtoXsgamma_legacy_SuperIso_SM_reference":.0003382457724,
  "legacy_BR_NP_minus_SM":legacy-.0003382457724,
  "legacy_BR_ratio_to_same_legacy_SM":legacy/.0003382457724,
  "A1U_source_diagnostics":fake_full_legacy(210.,680.,1.1,5.63),
  "modern_2026_NNLO_and_likelihood_validated":False,
  "full_Zee_allowed_excluded":None,
 }

def cohort():
 ids=list(g.PRIORITY)+[f"B4_{i:07d}" for i in range(303)]
 assert len(set(ids))==309
 return ids

class F6Contracts(unittest.TestCase):
 def test_no_physical_modern_2026_exclusion(self):
  self.assertIn("NOT_MODERN_CL",g.STATUS)
  self.assertEqual(len(g.PRIORITY),6)
  with tempfile.TemporaryDirectory() as d:
   rows=[fake_record(i) for i in cohort()]
   res=g.final(Path(d),rows,{"synthetic":True},.0003382457724,
               {"historical_controls":True})
   self.assertIsNone(res["Zee_allowed_or_excluded"])
   self.assertFalse(res["modern_2026_matching_and_theory_uncertainties_calibrated"])
   self.assertFalse(res["experimental_95CL_likelihood_validated"])
   self.assertEqual(len(res["priority_six"]),6)
   with (Path(d)/"F6_309_legacy_BR_HS_cascade_NO_CL.csv").open() as f:
    self.assertEqual(len(list(csv.DictReader(f))),309)

 def test_incomplete_309_rejected_and_false_exclusion_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   rows=[fake_record(i) for i in cohort()]
   with self.assertRaisesRegex(ValueError,"309 unique"):
    g.final(Path(d),rows[:-1],{},.000338,{})
   rows[0]["full_Zee_allowed_excluded"]=False
   with self.assertRaisesRegex(ValueError,"cannot manufacture"):
    g.final(Path(d),rows,{},.000338,{})

 def test_duplicate_original_inputs_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   rows=[fake_record(i) for i in cohort()]
   rows[-1]=rows[0].copy()
   with self.assertRaisesRegex(ValueError,"309 unique"):
    g.final(Path(d),rows,{},.000338,{})

 def test_original_F5_E7_model_crossjoin_and_tamper(self):
  ids=cohort()
  prior={k:fake_e7(k) for k in ids}
  with tempfile.TemporaryDirectory() as d:
   folder=Path(d);data=folder/g.F5_NAME
   with data.open("w") as f:
    for k in ids:f.write(json.dumps(fake_f5(k))+"\n")
   v={
    "status":g.F5_IMPORT_STATUS,
    "source_models":309,"F4b_source_matched_controls":8,
    "complete_EOS_NLO_matrix_elements_and_B_to_Xs_gamma_BR":False,
    "full_model_allowed_or_excluded":None,
    "source_provenance":{
      "F5_driver_SHA256":g.sha(g.ROOT/
       "scripts/zee_gateF5_309_source_pinned_C7_dipole_pareto.py")},
    "output_sha256":{data.name:g.sha(data)},
   }
   g.save(folder/"summary.json",v)
   g.save(folder/"manifest.json",{
      "status":v["status"],"source":v["source_provenance"],
      "summary_SHA256":g.sha(folder/"summary.json")})
   out,_=g.input_f5(folder,prior)
   self.assertEqual(len(out),309)
   with data.open("a") as f:f.write("{}\n")
   with self.assertRaisesRegex(ValueError,"SHA evidence"):
    g.input_f5(folder,prior)

 def test_A1U_original_source_point_passed_unchanged_to_driver(self):
  ids=cohort()
  seen=[]
  def mockrun(exe,m1,m2,gam,t,mode):
   seen.append((m1,m2,gam,t,mode))
   return fake_full_legacy(m1,m2,gam,t),"SUCCESS"
  with patch.object(g,"run_pinned",side_effect=mockrun):
   with contextlib.redirect_stdout(io.StringIO()):
    out=g.apply({k:fake_f5(k) for k in ids},
                Path("/home/fake"),"helper_reload",.0003382457724)
  self.assertEqual(len(out),309)
  self.assertEqual(len(seen),309)
  self.assertEqual(seen[0][4],"helper_reload")
  self.assertEqual(out[0]["F5_strict_C7eff_projector_not_rate"],.0199)
  self.assertTrue(all(not r["modern_2026_NNLO_and_likelihood_validated"]
                      and r["full_Zee_allowed_excluded"] is None for r in out))

 def test_A1U_model_mass_and_gamma_validity_rejected_before_source(self):
  for vals in ((150.,700.,1.,6.),(210.,200.,1.,6.),
               (200.,700.,-1.,6.),(210.,700.,2.,6.),
               (210.,700.,1.,101.)):
   with self.assertRaisesRegex(ValueError,"outside validated"):
    g.run_pinned(Path("/home/none"),*vals,"helper_reload")

 def test_A1U_Historical_Mixed_and_Endpoint_controls_must_close(self):
  controls={}
  ref_br=fake_full_legacy(300.,700.,1.089,5.597170833164245)
  keyruns=[
   (300.,700.,1.089),
   (300.,700.,0.),
   (300.,700.,math.pi/2),
   (700.,700.,1.089)]
  for m1,m2,ga in keyruns:
   controls[m1,m2,ga]=fake_full_legacy(m1,m2,ga,5.597170833164245)
  prev={
   "benchmark":ref_br,
   "gamma_0_endpoint":{
      "full_legacy_Zee_BR":controls[300.,700.,0.]["full_legacy_Zee_BR"]},
   "gamma_pi2_endpoint":{
      "full_legacy_Zee_BR":controls[300.,700.,math.pi/2]["full_legacy_Zee_BR"]},
   "equal_mass_gamma_endpoint":{
      "full_legacy_Zee_BR":controls[700.,700.,1.089]["full_legacy_Zee_BR"]},
  }
  def callback(exe,m1,m2,gam,t,mode):
   return controls[m1,m2,gam],"SUCCESS"
  with patch.object(g,"run_pinned",side_effect=callback):
   val=g.benchmark_closure(Path("/home/fake"),prev,"helper_reload")
   self.assertTrue(val["all_four_historical_A1U_controls_closed"])
   prev["benchmark"]["full_legacy_Zee_BR"]+=.00001
   with self.assertRaisesRegex(ValueError,"closure mismatch"):
    g.benchmark_closure(Path("/home/fake"),prev,"helper_reload")

if __name__=="__main__":unittest.main()
