"""F8: 309 genuine source-cohort 670 TypeII same-kernel vs mixing counterfactual tests.

No model exclusions; fake source callable only here; AF calls original A1U
SuperIso binary with complete 309 source SHA evidence.
"""
import csv,json,math,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing as x

LEGACY_SM=0.0003382457724040796
def fake_source(exe,m1,m2,g,t):
 # TypeII single-mass amplitude proxy with correct doublet weights;
 # intentionally unitary in degenerate mass and endpoints.
 w=math.cos(g)**2*(670./m1)**2+math.sin(g)**2*(670./m2)**2
 return LEGACY_SM+4.1e-5*w*(1+0.001*(t-5.6))

def point(k,i):
 m1=210.+i*.03;m2=690.+i*.05;g=1.1;t=5.6+i*.001
 b=fake_source(None,m1,m2,g,t)
 return {
  "candidate_id":k,"mH1_GeV":m1,"mH2_GeV":m2,
  "gamma":g,"tanbeta":t,
  "BR_BtoXsgamma_legacy_SuperIso_two_state":b,
  "BR_BtoXsgamma_legacy_SuperIso_SM_reference":LEGACY_SM,
  "legacy_BR_NP_minus_SM":b-LEGACY_SM,
  "HiggsSignals_E6_delta_chi2_NOT_CL":i*.01,
  "E7_included_cascade_proxy_NOT_physical_rate":.59-i*.0002,
  "full_Zee_allowed_excluded":None,
 }
IDS=list(x.PRIORITY)+[f"B4_{i:07d}" for i in range(303)]
assert len(set(IDS))==309
def sample():return {k:point(k,i) for i,k in enumerate(IDS)}

class F8Unit(unittest.TestCase):
 def test_1_original_309_compare_source_and_typeII670_per_tanbeta(self):
  data=sample()
  z=x.sweep_actual(data,Path("/home/fake"),call=fake_source)
  self.assertEqual(len(z),309)
  self.assertTrue(all(r["model_allowed_or_excluded"] is None for r in z))
  self.assertTrue(all(r["published_TypeII_670_bound_transferred_to_Zee"] is False
                      for r in z))
  for r in z:
   self.assertAlmostEqual(
    r["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"],
    (r["F6_original_legacy_inclusive_BR"]-LEGACY_SM)/
    (r["reference_TypeII_670_legacy_BR_same_tanbeta"]-LEGACY_SM))
   self.assertAlmostEqual(
    r["H1_quark_doublet_weight_cos2gamma"]+
    r["H2_quark_doublet_weight_sin2gamma"],1.)

 def test_2_exact_historical_benchmark_reproduction_before_any_scan(self):
  prev=sample()
  anchor=x.check_anchor(Path("/home/fake"),prev,call=fake_source)
  self.assertEqual(anchor["reproduced_F6_original_priority"],6)
  self.assertTrue(anchor["TypeII670_degenerate_H1_H2_gamma_independence_verified"])
  self.assertGreater(anchor["reference_BR_legacy"],LEGACY_SM)
  def corrupt(exe,m1,m2,g,t):
   v=fake_source(exe,m1,m2,g,t)
   if m1!=670. and m2!=670.:return v+1e-6
   return v
  with self.assertRaisesRegex(ValueError,"F8 source closure"):
   x.check_anchor(Path("/home/fake"),prev,call=corrupt)

 def test_3_exact_degenerate_TypeII_gamma_independence_required(self):
  prev=sample()
  def broken(exe,m1,m2,g,t):
   v=fake_source(exe,m1,m2,g,t)
   if m1==m2==670.:
    return v+g*1e-6
   return v
  with self.assertRaisesRegex(ValueError,"F8 source closure"):
   x.check_anchor(Path("/home/fake"),prev,call=broken)

 def test_4_counterfactual_scans_include_original_and_both_endpoints(self):
  scans=x.counterfactual_grid(sample(),Path("/home/fake"),
                              call=fake_source,ngrid=21)
  self.assertEqual(len(scans),6*22)
  self.assertEqual(sum(r["is_original_gamma_source_model"] for r in scans),6)
  self.assertTrue(all(
    r["counterfactual_scalar_potential_neutrinos_LFV_RGE_unverified"]
    and r["complete_cascade_BRs_not_recomputed"]
    and r["experimental_Zee_allowed_or_excluded"] is None
    for r in scans))
  for key in x.PRIORITY:
   mine=[z for z in scans if z["source_candidate_id"]==key]
   self.assertEqual(len(mine),22)
   self.assertEqual(mine[0]["gamma_counterfactual"],0.)
   self.assertAlmostEqual(mine[-1]["gamma_counterfactual"],math.pi/2)
   exact=[z for z in mine if z["is_original_gamma_source_model"]]
   self.assertEqual(len(exact),1)
   self.assertEqual(exact[0]["original_gamma"],exact[0]["gamma_counterfactual"])

 def test_5_false_counterfactual_cascade_claim_rejected(self):
  with self.assertRaisesRegex(ValueError,"mixing interval"):
   x.gauge_geometry(-.1)
  with self.assertRaisesRegex(ValueError,"mixing interval"):
   x.gauge_geometry(float("nan"))
  for gamma in (0.,math.pi/6,math.pi/4,math.pi/2):
   g=x.gauge_geometry(gamma)
   self.assertAlmostEqual(g["H1_quark_doublet_weight_cos2gamma"]+
                          g["H2_quark_doublet_weight_sin2gamma"],1.)
   self.assertAlmostEqual(
       g["offdiagonal_ZH1H2_squared_normalized_to_max"],math.sin(2*gamma)**2)
  self.assertAlmostEqual(x.gauge_geometry(math.pi/4)[
      "offdiagonal_ZH1H2_squared_normalized_to_max"],1.)

 def test_6_write_309_real_and_132_counterfactual_no_exclusions(self):
  orig=sample()
  actual=x.sweep_actual(orig,Path("/home/fake"),call=fake_source)
  scan=x.counterfactual_grid(orig,Path("/home/fake"),
                              call=fake_source,ngrid=21)
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)
   report=x.save_report(path,actual,scan,{"synthetic":True})
   self.assertEqual(report["original_F6_Zee_models"],309)
   self.assertEqual(report["number_fixed_mass_gamma_counterfactual_rows"],132)
   self.assertIsNone(report["fully_model_allowed_or_excluded"])
   self.assertFalse(report["published_2026_TypeII_mass_bound_imposed_on_Zee"])
   self.assertFalse(report["F8_2026_modern_model_likelihood_completed"])
   self.assertEqual(len(report["six_priority_actual_source"]),6)
   for f in ("F8_309_legacy_typeII_670_same_kernel_DIAGNOSTIC.csv",
             "F8_six_fixed_mass_gamma_counterfactual_NOT_MODEL_POINTS.csv"):
    self.assertTrue((path/f).exists())
   with (path/"F8_309_legacy_typeII_670_same_kernel_DIAGNOSTIC.csv").open() as f:
    self.assertEqual(len(list(csv.DictReader(f))),309)

 def test_7_no_partial_dup_or_false_model_allowed(self):
  orig=sample()
  actual=x.sweep_actual(orig,Path("/home/fake"),call=fake_source)
  scan=x.counterfactual_grid(orig,Path("/home/fake"),
                              call=fake_source,ngrid=21)
  with tempfile.TemporaryDirectory() as d:
   for rows in (actual[:-1],actual[:-1]+[actual[0]]):
    with self.assertRaisesRegex(ValueError,"invalid 309"):
     x.save_report(Path(d),rows,scan,{})
   damaged=[z.copy() for z in actual]
   damaged[0]["model_allowed_or_excluded"]=True
   with self.assertRaisesRegex(ValueError,"misleading"):
    x.save_report(Path(d),damaged,scan,{})
   damaged_scan=[z.copy() for z in scan]
   damaged_scan[0]["experimental_Zee_allowed_or_excluded"]=False
   with self.assertRaisesRegex(ValueError,"misleading"):
    x.save_report(Path(d),actual,damaged_scan,{})

 def test_8_archive_executable_sha_and_path_provenance(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d);exe=path/x.EXEC
   exe.write_text("synthetic binary")
   props={"source_sha256":"C_SRC","vendor_library_sha256":"LIB_SRC",
          "binary_sha256":x.digest(exe),
          "command":["gcc","-o",str(exe)]}
   summary={"status":x.F6_STATUS,
        "source_provenance":{"new_C_executable":props}}
   x.writejson(path/"summary.json",summary)
   x.writejson(path/"manifest.json",{
       "summary_SHA256":x.digest(path/"summary.json")})
   got,_=x.archive_bin(path)
   self.assertEqual(got,exe)
   exe.write_text("tampered")
   with self.assertRaisesRegex(ValueError,"binary"):
    x.archive_bin(path)

if __name__=="__main__":unittest.main()
