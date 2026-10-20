"""F5 synthetic 309-point actual source-contract closure without AF binary."""
import contextlib,io,json,math,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateF5_309_source_pinned_C7_dipole_pareto as f

def wc(m1,m2,t,g):
 # Fake 3-mode source low coefficients: true F3 is evaluated on AF.
 z={}
 nlo=[2.2+g/10,2.3+g/10,2.32+g/10]
 for mode in range(3):
  for op in range(1,9):
   z[mode,op]={"high_LO":0.,"high_NLO":0.,"low_LO":0.,
     "low_NLO":0.,"low_SM_LO":0.,"low_SM_NLO":0.}
  z[mode,7].update({"low_SM_LO":-.34,"low_SM_NLO":-3.2,
    "low_LO":-.01*(700/m2)-.002*(250/m1),
    "low_NLO":nlo[mode]})
  z[mode,8]["low_NLO"]=.017+mode*.002
  z[mode,4]["high_NLO"]=.01 if mode==2 else 0.
 return z

def fake_probe(exe,m1,m2,t,g):
 return wc(m1,m2,t,g)

def sample(i):
 return {"candidate_id":f"B4_{i:07d}",
         "mH1_GeV":200.+i*.1,"mH2_GeV":700.+i*.2,
         "tanbeta":5.6+i*.01,"gamma":1.1,
         "HS_delta_chi2_E6_vs_fixed_SM":i*.01,
         "charged_cascade_included_channel_proxy_NOT_physical_rate":
           .55-i*.0003,
         "claim_full_Zee_approved":None,
         "claim_HiggsBounds_excluded":None}

class F5Unit(unittest.TestCase):
 def test_strict_C7eff_order_split_closes_and_not_a_BR(self):
  v=f.response(wc(200.,700.,5.6,1.1),.22469749)
  self.assertAlmostEqual(
     v["Q7eff_NP_strictly_truncated_LO_plus_NLO"],
     v["Q7eff_NP_LO"]+
     v["Q7eff_NP_NLO_evolution_and_SM_baseline"]+
     v["Q7eff_NP_NLO_matching_total"])
  self.assertAlmostEqual(
     v["Q7eff_NP_NLO_matching_total"],
     v["Q7eff_NP_NLO_matching_fourquark_induced"]+
     v["Q7eff_NP_NLO_matching_dipoles_only"])
  self.assertTrue(v["NOT_inclusive_B_to_Xs_gamma_BR"])
  self.assertIsNone(v["model_excluded_allowed"])

 def test_bad_source_mode_is_rejected(self):
  z=wc(200.,700.,5.6,1.1)
  z[1,7]["low_LO"]+=.01
  with self.assertRaisesRegex(ValueError,"source/control closure"):
   f.response(z,.224)

 def test_all_8_TypeII_controls_must_close_before_309(self):
  pairs=((m,t) for m in (300.,580.,670.,1000.) for t in (5.6,50.))
  controls={}
  for m,t in pairs:
   v=f.response(wc(m,m,t,0.),.224)
   controls[m,t]={k:v[k] for k in f.F4B_CONTROL_KEYS}
  self.assertEqual(f.check_f4b_controls(fake_probe,object(),.224,controls),8)
  controls[300.,5.6]["Q7eff_NP_LO"]+=.01
  with self.assertRaisesRegex(ValueError,"closure mismatch"):
   f.check_f4b_controls(fake_probe,object(),.224,controls)

 def test_309_original_Zee_source_rows_then_never_exclude(self):
  xs={f"B4_{i:07d}":sample(i) for i in range(309)}
  with contextlib.redirect_stdout(io.StringIO()):
   out=f.apply(xs,object(),.224,probe_func=fake_probe)
  self.assertEqual(len(out),309)
  with tempfile.TemporaryDirectory() as d:
   result=f.finish(Path(d),out,8,{"synthetic":True})
   self.assertEqual(result["source_models"],309)
   self.assertIsNone(result["full_model_allowed_or_excluded"])
   self.assertFalse(result["complete_EOS_NLO_matrix_elements_and_B_to_Xs_gamma_BR"])
   self.assertTrue((Path(d)/"F5_309_HS_cascade_C7_dipole_NO_EXCLUSION.csv").exists())
   with self.assertRaisesRegex(ValueError,"incomplete"):
    f.finish(Path(d),out[:-1],8,{})

 def test_F5_rejects_control_without_complete_validation(self):
  xs={f"B4_{i:07d}":sample(i) for i in range(309)}
  with contextlib.redirect_stdout(io.StringIO()):
   out=f.apply(xs,object(),.224,probe_func=fake_probe)
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,"8 controls missing"):
    f.finish(Path(d),out,7,{})

 def test_E7_must_be_309_and_SHA_pinned(self):
  with tempfile.TemporaryDirectory() as td:
   folder=Path(td)
   archive=folder/f.E7_FILE
   with archive.open("w") as stream:
    for i in range(309):
     stream.write(json.dumps(sample(i))+"\n")
   src=Path(f.ROOT/"scripts/zee_gateE7_309_general_lepton_width_pareto.py")
   pp={"E7_source_SHA256":f.sha(src),
       "original_E6_physics_sources":{"synthetic":True}}
   s={"status":"E7_309_NEUTRINO_CLOSED_GENERAL_ZEE_CHARGED_WIDTH_PARETO_NOT_ALLOWED",
      "original_models":309,"neutrino_closure_full_309_checked":True,
      "HiggsBounds_model_exclusion_not_evaluated":True,
      "full_allowed_and_excluded_Zee_counts":None,
      "source_provenance":pp,
      "sha256_outputs":{archive.name:f.sha(archive)}}
   f.save(folder/"summary.json",s)
   f.save(folder/"manifest.json",{"status":s["status"],
     "source":pp,"summary_SHA256":f.sha(folder/"summary.json")})
   rows,source=f.source_e7(folder)
   self.assertEqual(len(rows),309)
   self.assertEqual(source["E7_evidence_SHA256"],f.sha(archive))
   with archive.open("a") as stream:stream.write("{}\n")
   with self.assertRaisesRegex(ValueError,"SHA mismatch"):
    f.source_e7(folder)

 def test_E7_unknown_flags_and_proxy_limits_protected(self):
  with tempfile.TemporaryDirectory() as td:
   folder=Path(td);archive=folder/f.E7_FILE
   x=[sample(i) for i in range(309)]
   x[0]["claim_HiggsBounds_excluded"]=True
   with archive.open("w") as stream:
    for z in x:stream.write(json.dumps(z)+"\n")
   pp={"E7_source_SHA256":f.sha(
          f.ROOT/"scripts/zee_gateE7_309_general_lepton_width_pareto.py")}
   s={"status":"E7_309_NEUTRINO_CLOSED_GENERAL_ZEE_CHARGED_WIDTH_PARETO_NOT_ALLOWED",
      "original_models":309,"neutrino_closure_full_309_checked":True,
      "HiggsBounds_model_exclusion_not_evaluated":True,
      "full_allowed_and_excluded_Zee_counts":None,
      "source_provenance":pp,"sha256_outputs":{archive.name:f.sha(archive)}}
   f.save(folder/"summary.json",s)
   f.save(folder/"manifest.json",{"status":s["status"],
      "source":pp,"summary_SHA256":f.sha(folder/"summary.json")})
   with self.assertRaisesRegex(ValueError,"invalid duplicate"):
    f.source_e7(folder)

if __name__=="__main__":unittest.main()
