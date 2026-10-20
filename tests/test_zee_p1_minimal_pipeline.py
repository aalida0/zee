"""Minimal Priority1 contract tests. No false model exclusions."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_p1_minimal_pipeline as p

class PriorityOne(unittest.TestCase):
 def test_component_inventory_exact(self):
  self.assertEqual(set(p.REQUIRED),set(p.KNOWN))
  self.assertEqual(len(p.REQUIRED),5)
  for value in p.KNOWN.values():
   self.assertTrue(value["missing"])

 def test_empty_inputs_not_accepted(self):
  with self.assertRaises(ValueError):p.evaluate({})
  with self.assertRaises(ValueError):p.evaluate({"id":"a"},{"unknown":{}})
  with self.assertRaises(ValueError):p.evaluate({"id":"a"},{"higgs":[]})

 def test_default_fails_closed(self):
  x=p.evaluate({"id":"B4_0004143"})
  self.assertIsNone(x["experimental_allowed_or_excluded"])
  self.assertFalse(x["all_required_implemented_and_validated"])
  self.assertEqual(set(x["components"]),set(p.REQUIRED))
  self.assertTrue(all(z["status"]=="NOT_IMPLEMENTED_COMPLETE"
                      for z in x["components"].values()))

 def test_claim_of_validation_not_enough(self):
  supplied={k:{"status":"validated"} for k in p.REQUIRED}
  x=p.evaluate({"id":"benchmark"},supplied)
  self.assertTrue(all(q["status"]=="SUPPLIED_NOT_CERTIFIED"
                      for q in x["components"].values()))
  self.assertIsNone(x["experimental_allowed_or_excluded"])

 def test_even_hashed_external_claim_cannot_invent_exclusion(self):
  ev={"status":"validated","validation":{
      "independent_comparison_passed":True,
      "complete_model_basis":True,"reference":"external-paper",
      "source_sha256":"a"*64}}
  x=p.evaluate({"id":"x"},{k:ev for k in p.REQUIRED})
  self.assertFalse(x["all_required_implemented_and_validated"])
  self.assertIsNone(x["experimental_allowed_or_excluded"])
  self.assertEqual({v["status"] for v in x["components"].values()},
     {"EXTERNAL_VALIDATION_CLAIM_REQUIRES_INDEPENDENT_REVIEW"})

 def test_cli_multiple_points_and_sha(self):
  import subprocess
  with tempfile.TemporaryDirectory() as d:
   inp=Path(d)/"inputs.jsonl";out=Path(d)/"results.jsonl"
   inp.write_text('{"id":"a"}\n{"id":"b"}\n')
   run=subprocess.run([sys.executable,p.__file__,"--points",str(inp),
                     "--output",str(out)],capture_output=True,text=True)
   self.assertEqual(run.returncode,0,msg=run.stderr)
   self.assertEqual(len(out.read_text().splitlines()),2)
   self.assertIn("MODEL_EXCLUSIONS 0",run.stdout)
   run2=subprocess.run([sys.executable,p.__file__,"--points",str(inp),
                     "--output",str(out)],capture_output=True,text=True)
   self.assertNotEqual(run2.returncode,0)

 def test_duplicate_ids_fail_without_published_partial_output(self):
  import subprocess
  with tempfile.TemporaryDirectory() as d:
   inp=Path(d)/"in.jsonl";out=Path(d)/"out.jsonl"
   inp.write_text('{"id":"a"}\n{"id":"a"}\n')
   run=subprocess.run([sys.executable,p.__file__,"--points",str(inp),
        "--output",str(out)],capture_output=True,text=True)
   self.assertNotEqual(run.returncode,0)
   self.assertFalse(out.exists())
   self.assertFalse((Path(d)/"out.jsonl.partial").exists())

if __name__=="__main__":unittest.main()
