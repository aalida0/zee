"""F9: source-locked 309 original + 132 counterfactual F8 flavor/gauge regressions.

CI is intentionally independent of AF F8 output and SuperIso: it constructs
a complete *synthetic* F8 archive using the real F8 code and a fake analytic
legacy response with correct equal-mass gamma unitarity. The full one-shot
AF test opens the ORIGINAL source-computed F8 archive with SHA checks.
"""
import contextlib,csv,io,json,math,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing as old
import zee_gateF9_F8_mixing_flavor_geometry_132 as f

SM=.0003382457724040796
IDS=list(old.PRIORITY)+[f"B4_{i:07d}" for i in range(303)]
assert len(set(IDS))==309

def fake_legacy(exe,m1,m2,g,t):
 c=math.cos(g)**2;s=math.sin(g)**2
 return SM+4.2e-5*(c*(670/m1)**2+s*(670/m2)**2)*(1+.0005*(t-5.6))

def src(k,i):
 m1=207.+i*.04;m2=695.+i*.07
 gamma=1.1+(i%4)*.01;t=5.64+(i%5)*.001
 return {
  "candidate_id":k,
  "mH1_GeV":m1,"mH2_GeV":m2,
  "gamma":gamma,"tanbeta":t,
  "BR_BtoXsgamma_legacy_SuperIso_two_state":
    fake_legacy(None,m1,m2,gamma,t),
  "BR_BtoXsgamma_legacy_SuperIso_SM_reference":SM,
  "HiggsSignals_E6_delta_chi2_NOT_CL":i*.005,
  "E7_included_cascade_proxy_NOT_physical_rate":.6-i*.0002,
 }

def archive(path):
 original={k:src(k,i) for i,k in enumerate(IDS)}
 with contextlib.redirect_stdout(io.StringIO()):
  actual=old.sweep_actual(original,Path("/home/synthetic"),call=fake_legacy)
 slices=old.counterfactual_grid(original,Path("/home/synthetic"),
                                call=fake_legacy)
 proof={"F8_script_SHA256":f.digest(
    f.ROOT/"scripts/zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing.py"),
        "synthetic":True}
 old.save_report(path,actual,slices,proof)
 f.dumpjson(path/"manifest.json",{
  "status":old.STATUS,"source":proof,
  "summary_SHA256":f.digest(path/"summary.json")})

class F9Unit(unittest.TestCase):
 def test_full_f8_archive_309_132_hash_closure(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d);archive(path)
   actual,grids,source=f.read_f8(path)
   self.assertEqual(len(actual),309)
   self.assertEqual(sum(map(len,grids.values())),132)
   self.assertEqual(set(grids),set(f.PRIORITY))
   self.assertIn("F8_outputs_SHA256",source)
   self.assertTrue(source["source_typeII_670_comparator_is_not_a_Zee_CL"])
   self.assertEqual(sum(x["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"]>1
                        for x in actual.values()),309)

 def test_f8_archived_SHA_tampering_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d);archive(path)
   with (path/f.F8_GAMMA).open("a") as h:
    h.write("\n")
   with self.assertRaisesRegex(ValueError,"archived SHA mismatch"):
    f.read_f8(path)

 def test_f8_mixed_gamma_geometry_tampering_rejected_after_resigning_hash(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d);archive(path)
   p=path/f.F8_GAMMA
   with p.open(newline="") as h:
    rows=list(csv.DictReader(h))
    fields=list(rows[0])
   rows[0]["offdiagonal_ZH1H2_squared_normalized_to_max"]="0.8"
   with p.open("w",newline="") as h:
    w=csv.DictWriter(h,fieldnames=fields)
    w.writeheader();w.writerows(rows)
   summary=f.readjson(path/"summary.json")
   summary["sha256_outputs"][p.name]=f.digest(p)
   f.dumpjson(path/"summary.json",summary)
   manifest=f.readjson(path/"manifest.json")
   manifest["summary_SHA256"]=f.digest(path/"summary.json")
   f.dumpjson(path/"manifest.json",manifest)
   with self.assertRaisesRegex(ValueError,"geometric"):
    f.read_f8(path)

 def test_six_real_original_points_are_restored_exactly(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d);archive(path)
   actual,grids,_=f.read_f8(path)
   grid,front,groups=f.evaluate(actual,grids)
   self.assertEqual(len(grid),132)
   self.assertEqual(sum(v["is_original_physically_reconstructed_Zee_point"]
                        for v in grid),6)
   for k in f.PRIORITY:
    self.assertAlmostEqual(groups[k][
      "original_legacy_Zee_over_TypeII670_NP_shift_ratio"],
      actual[k]["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"])
    orig=[v for v in grid if v["source_candidate_id"]==k
          and v["is_original_physically_reconstructed_Zee_point"]]
    self.assertEqual(len(orig),1)
    self.assertAlmostEqual(orig[0][
       "offdiag_Z_gauge_squared_relative_to_original"],1.)
    self.assertAlmostEqual(orig[0][
       "prodweighted_gauge_geometry_relative_to_original_NOT_signal_rate"],1.)

 def test_no_counterfactual_is_a_physical_acceptance(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d);archive(path)
   original,scans,proof=f.read_f8(path)
   grid,front,groups=f.evaluate(original,scans)
   self.assertTrue(all(v["experimental_allowed_or_excluded"] is None
      and v["modern_2026_matching_or_exclusion_provided"] is False
      and v["complete_Zee_scalar_flavor_reoptimized_for_counterfactual"] is False
      and v["actual_included_cascade_fraction_for_gamma_recalculated"] is False
      for v in grid))
   with tempfile.TemporaryDirectory() as out:
    report=f.output(Path(out),original,grid,front,groups,proof)
    self.assertIsNone(report["full_Zee_allowed_excluded"])
    self.assertFalse(report[
      "modern_2026_Zee_B_to_Xs_gamma_complete_model_likelihood_evaluated"])
    self.assertEqual(report["archived_original_Zee_points"],309)
    self.assertEqual(report["archived_gamma_counterfactual_rows"],132)
    self.assertEqual(len(report["six_priority_summaries"]),6)
    self.assertTrue((Path(out)/
       "F9_132_gamma_legacy_flavor_gauge_geometry_NOT_PHYSICAL.csv").exists())
    grid[0]["experimental_allowed_or_excluded"]=True
    with self.assertRaisesRegex(ValueError,"may not claim"):
     f.output(Path(out),original,grid,front,groups,{})

 def test_pareto_gamma_dominance_and_identical_ties(self):
  base={
    "source_candidate_id":"test",
    "gamma_counterfactual_rad":0.
  }
  data=[
    {**base,"gamma_counterfactual_rad":.1,
     "legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL":.8,
     "offdiag_Z_gauge_squared_relative_to_original":.2},
    {**base,"gamma_counterfactual_rad":.2,
     "legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL":.8,
     "offdiag_Z_gauge_squared_relative_to_original":.1},
    {**base,"gamma_counterfactual_rad":.3,
     "legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL":.9,
     "offdiag_Z_gauge_squared_relative_to_original":.6},
    {**base,"gamma_counterfactual_rad":.4,
     "legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL":1.,
     "offdiag_Z_gauge_squared_relative_to_original":.4},
  ]
  front=f.pareto(data)
  self.assertEqual([round(q["gamma_counterfactual_rad"],2)
                    for q in front],[.1,.3])

 def test_f9_gauge_and_production_weighted_geometry_not_a_rate(self):
  gamma=math.asin(math.sqrt(2/3))
  grid=f.gauge_geometry(gamma)
  p=math.sin(gamma)**2*grid[
     "offdiagonal_ZH1H2_squared_normalized_to_max"]
  # Maximizes x*4x(1-x) over x=sin²gamma.
  self.assertAlmostEqual(p,16/27)
  self.assertAlmostEqual(f.gauge_geometry(math.pi/4)[
    "offdiagonal_ZH1H2_squared_normalized_to_max"],1.)
  self.assertAlmostEqual(f.gauge_geometry(math.pi/2)[
    "offdiagonal_ZH1H2_squared_normalized_to_max"],0.,places=12)
  self.assertEqual(f.RETENTION_THRESHOLDS,(.5,.8,.95))

 def test_wrong_original_row_flag_rejected_even_if_resigned(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d);archive(path)
   p=path/f.F8_GAMMA
   with p.open(newline="") as h:
    rows=list(csv.DictReader(h))
    fields=list(rows[0])
   rr=next(q for q in rows if q[
     "is_original_gamma_source_model"]=="True")
   rr["is_original_gamma_source_model"]="False"
   with p.open("w",newline="") as h:
    w=csv.DictWriter(h,fieldnames=fields)
    w.writeheader();w.writerows(rows)
   s=f.readjson(path/"summary.json")
   s["sha256_outputs"][p.name]=f.digest(p)
   f.dumpjson(path/"summary.json",s)
   m=f.readjson(path/"manifest.json")
   m["summary_SHA256"]=f.digest(path/"summary.json")
   f.dumpjson(path/"manifest.json",m)
   with self.assertRaisesRegex(ValueError,"mislabeled|missing original"):
    f.read_f8(path)

if __name__=="__main__":
 unittest.main()
