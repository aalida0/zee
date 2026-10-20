"""E7 fail-closed source/physics accounting and 309-case Pareto regressions.

No actual E2-E6 artifacts/HSDataSet are bundled in these unit fixtures; the
full AF integration runner reopens and SHA-checks all original results.
"""
import csv,json,math,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateE7_309_general_lepton_width_pareto as g


def toy(i,chi=None,cascade=None):
 return {
  "candidate_id":f"B4_{i:07d}",
  "mH1_GeV":210.,"mH2_GeV":700.,"gamma":1.2,"tanbeta":6.,
  "HS_delta_chi2_E6_vs_fixed_SM":float(i/100 if chi is None else chi),
  "original_B4_nonleptonic_proxy":.55,
  "charged_cascade_included_channel_proxy_NOT_physical_rate":
      float(i/1000 if cascade is None else cascade),
  "corrected_minus_original_B4_proxy":float(i/1000-.55),
  "included_channel_BR_H2_to_H1Z":.7,
  "included_channel_BR_H1_to_tb":.9,
  "charged_included_total_H1_GeV":4.,
  "charged_included_total_H2_GeV":5.,
  "charged_lepton_widths_by_flavour_GeV":{},
  "charged_partial_widths_included_GeV":{},
  "neutrino_matrix_reconstruction_max_abs_eV":0.,
  "partial_LFV_selected_D4_NOT_complete_likelihood":.1,
  "claim_full_Zee_approved":None,
  "claim_HiggsBounds_excluded":None,
  "complete_width_or_production_certified":False,
 }

class E7Regressions(unittest.TestCase):
 def test_pareto_enforces_two_objective_domination_and_ties(self):
  r=[toy(0,0,.2),toy(1,1,.5),toy(2,1,.4),
     toy(3,3,.7),toy(4,4,.65),toy(5,2,.7),
     toy(6,-1,.05),toy(7,0,.2)]
  ids=[x["candidate_id"] for x in g.pareto(r)]
  self.assertEqual(ids,["B4_0000006","B4_0000000",
                       "B4_0000001","B4_0000005"])
  self.assertEqual(len(ids),len(set(ids)))

 def test_e7_never_returns_exclusion_or_statistical_CL(self):
  self.assertIn("NOT_ALLOWED",g.STATUS)
  self.assertIn("NOT_EVALUATED",g.MISSING["full_HiggsBounds_Zee"])
  with tempfile.TemporaryDirectory() as d:
   data=[toy(i) for i in range(309)]
   summary=g.write_outputs(Path(d),data,{"synthetic":True},.2)
   self.assertEqual(summary["original_models"],309)
   self.assertIsNone(summary["full_allowed_and_excluded_Zee_counts"])
   self.assertTrue(summary["HiggsBounds_model_exclusion_not_evaluated"])
   self.assertEqual(sum(x["claim_full_Zee_approved"] is not None
                        for x in data),0)
   with (Path(d)/"E7_309_HS_vs_lepton_corrected_cascade_NOT_ALLOWED.csv").open() as fh:
    result=list(csv.DictReader(fh))
   self.assertEqual(len(result),309)
   self.assertEqual(summary["Pareto_frontier_count"],309)
   self.assertTrue((Path(d)/"E7_Pareto_HS_vs_general_Zee_cascade_NOT_ALLOWED.csv").exists())
   self.assertTrue(all(x["claim_HiggsBounds_excluded"] is None for x in data))

 def test_incomplete_or_duplicate_cohort_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   a=[toy(i) for i in range(309)]
   for case in (a[:-1],a[:-1]+[a[0]]):
    with self.assertRaisesRegex(ValueError,"309 unique"):
     g.write_outputs(Path(d),case,{},.4)

 def test_nonfinite_or_unphysical_values_fail_closed(self):
  with self.assertRaisesRegex(ValueError,"Nonfinite"):
   g.pareto([toy(1,chi=float("nan"))])
  with self.assertRaisesRegex(ValueError,"outside"):
   with tempfile.TemporaryDirectory() as d:
    g.write_outputs(Path(d),[toy(i) for i in range(309)],{},1.1)
  with tempfile.TemporaryDirectory() as d:
   a=[toy(i) for i in range(309)]
   a[0]["claim_HiggsBounds_excluded"]=True
   with self.assertRaisesRegex(ValueError,"False HiggsBounds"):
    g.write_outputs(Path(d),a,{},.1)

 def synthetic_archive(self,d,corrupt=None):
  src={"e6_source":"SOURCE","e6_status":"E6_ACTUAL_SUCCESS"}
  folder=Path(d)
  j=folder/g.E6_JSON;c=folder/g.E6_CSV
  rows=[{
      "candidate_id":f"B4_{i:07d}",
      "delta_chisq_vs_same_SM":i*.1,
      "loop_amplitudes":{
        "new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio":1.05},
      "h_Zgamma_full_one_loop_charged_scalar_mixed_mass_completed":True,
      "full_Zee_allowed_or_excluded":None,
  } for i in range(309)]
  if corrupt=="duplicate":rows[-1]=rows[0].copy()
  with j.open("w") as f:
   for row in rows:f.write(json.dumps(row)+"\n")
  with c.open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=["candidate_id",
                                   "gamma_Zgamma_loop_corrected_delta_vs_SM"])
   w.writeheader()
   for i in range(309):
    w.writerow({"candidate_id":f"B4_{i:07d}",
                "gamma_Zgamma_loop_corrected_delta_vs_SM":i*.1})
  data={
   "status":src["e6_status"],
   "original_source_models":309,
   "updated_HiggsSignals_hgamma_gamma_models":309,
   "same_HiggsSignals_observables":159,
   "full_Zee_allowed_or_excluded":None,
   "full_h_to_Zgamma_one_loop_scalar_subset_with_mixed_mass_completed":True,
   "full_h_to_Zgamma_higher_order_model_prediction_NOT_completed":True,
   "source":src["e6_source"],
   "output_hashes":{j.name:g.digest(j),c.name:g.digest(c)},
  }
  g.save(folder/"summary.json",data)
  g.save(folder/"manifest.json",{
      "status":src["e6_status"],
      "source":{"source":src["e6_source"]},
      "summary_SHA256":g.digest(folder/"summary.json"),
  })
  return src

 def test_E6_all_309_rows_and_physics_hashes_are_required(self):
  with tempfile.TemporaryDirectory() as d:
   src=self.synthetic_archive(d)
   cohort={f"B4_{i:07d}" for i in range(309)}
   rows,proof=g.validate_e6_archive(Path(d),cohort,src)
   self.assertEqual(len(rows),309)
   self.assertIn("E6_JSONL_SHA256",proof)
   with (Path(d)/g.E6_JSON).open("a") as f:
    f.write("{}\n")
   with self.assertRaisesRegex(ValueError,"SHA mismatch"):
    g.validate_e6_archive(Path(d),cohort,src)

 def test_E6_reject_wrong_source_and_duplicate(self):
  with tempfile.TemporaryDirectory() as d:
   src=self.synthetic_archive(d)
   cohort={f"B4_{i:07d}" for i in range(309)}
   with self.assertRaisesRegex(ValueError,"source files changed"):
    g.validate_e6_archive(Path(d),cohort,{
        "e6_status":src["e6_status"],"e6_source":"DIFFERENT"})
  with tempfile.TemporaryDirectory() as d:
   src=self.synthetic_archive(d,corrupt="duplicate")
   cohort={f"B4_{i:07d}" for i in range(309)}
   with self.assertRaisesRegex(ValueError,"duplicate"):
    g.validate_e6_archive(Path(d),cohort,src)

 def test_charged_widths_no_legacy_typeii_leptons_and_no_oversumming(self):
  fakevec=lambda M,m,mv,c: max(0.,M-m-mv)*c*c
  fake6=types.ModuleType("gate6_width_inventory")
  fake6.vector_width=fakevec
  fake6.MZ=91.1876
  fakeb3=types.ModuleType("gateB3_general_zee_charged_lepton_widths")
  fakeb3.LEPTONS=("e","mu","tau")
  fakeD5=types.ModuleType("zee_gateD5_h125_direct_LFV_27")
  fakeD5.VEV=246.21965
  scalar={"mH1":200.,"mH2":670.,"gamma":1.1}
  H2Z=fakevec(670.,200.,fake6.MZ,
       fake6.MZ/fakeD5.VEV*math.sin(1.1)*math.cos(1.1))
  widths={"H1":{"tb":3.,"e_nu_generalZee":.01,
                  "mu_nu_generalZee":.02,"tau_nu_generalZee":.03},
          "H2":{"H1_Z":H2Z,"tb":4.,"e_nu_generalZee":.04,
                  "mu_nu_generalZee":.05,"tau_nu_generalZee":.06}}
  T={k:sum(v.values()) for k,v in widths.items()}
  br2=H2Z/T["H2"];br1=3/T["H1"]
  row={"partial_widths_included_GeV":widths,
       "totals_included_GeV":T,
       "BR_H2_H1Z_included_general_Zee":br2,
       "BR_H1_tb_included_general_Zee":br1,
       "production_weighted_partial_cascade_proxy":
           math.sin(1.1)**2*br2*br1}
  with patch.dict(sys.modules,{
        "gate6_width_inventory":fake6,
        "gateB3_general_zee_charged_lepton_widths":fakeb3,
        "zee_gateD5_h125_direct_LFV_27":fakeD5}):
   got=g.numerical_channel_closure(scalar,row)
   self.assertAlmostEqual(got,math.sin(1.1)**2*br2*br1)
   broken={**row,"partial_widths_included_GeV":{
      **widths,"H1":{**widths["H1"],"tau_nu_TypeII":.3}}}
   with self.assertRaisesRegex(ValueError,"lepton width replacement"):
    g.numerical_channel_closure(scalar,broken)
   broken={**row,"totals_included_GeV":{**T,"H2":T["H2"]+1.}}
   with self.assertRaisesRegex(ValueError,"closure"):
    g.numerical_channel_closure(scalar,broken)

if __name__=="__main__":
 unittest.main()
