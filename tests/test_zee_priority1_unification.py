"""Priority1 consolidated CLI, actual-source widths and generator rate ingestion."""
import contextlib,csv,io,json,math,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_priority1_streaming as stream
import zee_priority1_charged_width_export as widths
import zee_priority1_production_lhe as lhe
import zee_priority1_cli as cli

class TestP1Unification(unittest.TestCase):
 def test_stream_one_canonical_cli_csv_and_jsonl(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for ext,payload in (
       (".csv","id,mH1,mH2,gamma,candidate_status\nB4_test,220,700,1.1,SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED\n"),
       (".jsonl",'{"id":"B4_one","mH1":220,"mH2":700}\n{"id":"B4_two","mH1":300,"mH2":800}\n')):
    src=root/("source"+ext);out=root/("output"+ext.replace(".","_"))
    src.write_text(payload)
    with contextlib.redirect_stdout(io.StringIO()):
     self.assertEqual(cli.main(["--points",str(src),"--out",str(out),
                                "--stream-coverage"]),0)
    report=json.loads((out/"summary.json").read_text())
    self.assertEqual(report["original_candidate_count"],
                     1 if ext==".csv" else 2)
    self.assertIsNone(report["full_Zee_allowed_or_excluded"])
    self.assertEqual(len((out/"per_candidate.jsonl").read_text().splitlines()),
                     report["original_candidate_count"])
    self.assertFalse(report["scalar_physics_evaluated"])

 def test_duplicate_fails_closed_and_never_publishes_partial_data(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);data=root/"input.jsonl";out=root/"output.jsonl"
   data.write_text('{"id":"same"}\n{"id":"same"}\n')
   with self.assertRaises(Exception):
    stream.scan(data,out)
   self.assertFalse(out.exists())
   self.assertFalse(list(root.glob("p1_scan_*")))
   with self.assertRaises(ValueError):
    stream.structural({"id":"BAD","candidate_status":"ALLOWED"},False)

 def test_scalar_flag_invokes_true_existing_screen_interfaces(self):
  import sys,types
  # Fake modules only to validate stage plumbing (real AF physics tested
  # through existing gateB4 tests and actual --scalar-physics runs).
  fake=types.ModuleType("gateB4_adaptive_zee_scalar_scan")
  fake.scalar_screen=lambda z: {"max_abs_unitarity_eigenvalue":1}
  fake.ewpo_screen=lambda z,n: {"quadrature":n}
  row={"id":"SCALAR"}
  row.update({v:1. for v in stream.SCALAR_FIELDS})
  row["mH1"]=220;row["mH2"]=710;row["gamma"]=1.
  with unittest.mock.patch.dict(sys.modules,{"gateB4_adaptive_zee_scalar_scan":fake}):
   self.assertEqual(stream.structural(row,True)["scalar_EWPO_screen"],
     "PASSED_IMPLEMENTED_SCALAR_AND_STU_NOT_MODEL_ALLOWED")
  row.pop("k12")
  with self.assertRaises(KeyError):
   stream.structural(row,True)

 def test_e3_b3_partial_real_topology_is_not_complete_higgsbounds(self):
  name="B4_0004143"
  point={"id":name,"mH1":209.,"mH2":681.,"gamma":1.12}
  e3={"candidate_id":name,"full_Zee_allowed_or_excluded":None,
    "diagnostic_status":"MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED",
    "D2":{"chosen_optimized_source":{"solution":{
      "candidate_id":name,"f":"synthetic","Y":"synthetic"}}}}
  def backend(p,sol):
   self.assertEqual(sol["candidate_id"],name)
   c1={"tb":1.,"e_nu_generalZee":.01,
       "mu_nu_generalZee":.02,"tau_nu_generalZee":.03}
   c2={"H1_Z":3.,"tb":.2,"e_nu_generalZee":.01,
       "mu_nu_generalZee":.02,"tau_nu_generalZee":.03}
   return {"candidate_id":name,
       "status":"GENERAL_ZEE_LEPTON_WIDTHS_LO_INCLUDED_ONLY_NOT_ALLOWED",
       "neutrino_matrix_closure_eV":1e-15,
       "partial_widths_included_GeV":{"H1":c1,"H2":c2},
       "totals_included_GeV":{"H1":sum(c1.values()),"H2":sum(c2.values())},
       "BR_H2_H1Z_included_general_Zee":3/sum(c2.values()),
       "BR_H1_tb_included_general_Zee":1/sum(c1.values()),
       "production_weighted_partial_cascade_proxy":
            math.sin(p["gamma"])**2*3/sum(c2.values())/sum(c1.values())}
  output=widths.calculate(point,e3,backend=backend)
  self.assertFalse(output["all_physical_decay_channels_enumerated"])
  self.assertFalse(output["neutral_H_and_A_widths_computed"])
  self.assertIsNone(output["experimentally_allowed_or_excluded"])
  self.assertEqual(output["charged_included_LO_GeV"]["H2"]["H1_Z"],3.)
  broken=dict(e3);broken["D2"]={"chosen_optimized_source":{
    "solution":{"candidate_id":"other"}}}
  with self.assertRaisesRegex(ValueError,"source ID mismatch"):
   widths.calculate(point,broken,backend=backend)

 def test_e3_missing_solution_is_not_excluded(self):
  r=widths.calculate({"id":"some"},{"candidate_id":"some",
     "diagnostic_status":"INSUFFICIENT_SAVED_B2_FAMILIES_NOT_PHYSICAL_EXCLUSION",
     "full_Zee_allowed_or_excluded":None})
  self.assertEqual(r["status"],"BLOCKED_NO_OPTIMIZED_E3_FY")
  self.assertIsNone(r["experimentally_allowed_or_excluded"])

 def test_real_LHE_init_13000_source_and_strict_cross_section(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);src=root/"events.lhe"
   src.write_text("""<LesHouchesEvents version="3.0">
<init>
2212 2212 6500 6500 0 0 0 0 3 2
1.25E-02 1.0E-04 2.0E-02 1001
2.75E-02 2.0E-04 3.0E-02 1002
</init>
<event>
</event>
</LesHouchesEvents>""")
   z=lhe.parse_lhe_init(src)
   self.assertEqual(z["collider"],"LHC13")
   self.assertAlmostEqual(z["LHE_total_generator_reported_sigma_pb"],.04)
   self.assertEqual(len(z["partonic_subprocesses_LHE_init"]),2)
   (root/"process.dat").write_text("generate p p > h2+ t b~\n")
   (root/"param.dat").write_text("BLOCK MASS\n")
   spec={"runs":[{"candidate_id":"B4_C","state":"H2",
        "mode":"pp_to_H2_tb","lhe":str(src),
        "process_card":str(root/"process.dat"),
        "parameter_card":str(root/"param.dat"),
        "generator":"MG5_aMC","model":"Zee_model_not_independently_validated"}]}
   manifest=root/"runs.json";manifest.write_text(json.dumps(spec))
   target=root/"actual_partial_production.json"
   output=lhe.build(manifest,target)
   self.assertEqual(output["models_with_some_real_generator_LHE_rates"],1)
   self.assertFalse(output["validated_complete_Zee_production"])
   rows=json.loads(target.read_text())["records"]
   self.assertEqual(rows[0]["particles"]["H2"]["pp_to_H2_tb"]["collider"],"LHC13")
   self.assertIsNone(rows[0]["physical_Zee_allowed_or_excluded"])
   with self.assertRaisesRegex(ValueError,"overwrite"):
    lhe.build(manifest,target)

 def test_reject_unsupported_LHE_source(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/"e.lhe"
   file.write_text("<init>\n11 -11 6500 6500 0 0 0 0 3 1\n1 0 2 1\n</init>\n")
   with self.assertRaisesRegex(ValueError,"proton-proton"):
    lhe.parse_lhe_init(file)
   file.write_text("<init>\n2212 2212 5000 5000 0 0 0 0 3 1\n1 0 2 1\n</init>\n")
   with self.assertRaisesRegex(ValueError,"Unsupported"):
    lhe.parse_lhe_init(file)
   file.write_text("<init>\n2212 2212 6500 6500 0 0 0 0 3 1\n-1 0 2 1\n</init>\n")
   with self.assertRaisesRegex(ValueError,"Negative"):
    lhe.parse_lhe_init(file)

if __name__=="__main__":
 unittest.main()
