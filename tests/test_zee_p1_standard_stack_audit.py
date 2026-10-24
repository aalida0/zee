"""Standard-toolchain model readiness: no binary == validated Zee physics."""
import argparse,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_p1_standard_stack_audit import (
 STATUS,SARAH_FILES,command_info,sarah_model_info,tool_status,main)

def opts(**kw):
 vals=dict(sarah_model_dir=None,sarah_package_dir=None,
  spheno_model_executable=None,flexible_model_executable=None,
  bsmart_bin=None,mg5_bin=None,vevacious_bin=None)
 vals.update(kw)
 return argparse.Namespace(**vals)

class ExternalHEPStack(unittest.TestCase):
 def test_no_source_no_false_sarah_or_exclusion(self):
  z=tool_status(opts())
  self.assertEqual(z["status"],STATUS)
  self.assertFalse(z["sources"]["SARAH_model"]["detected"])
  self.assertFalse(z["model_compile_and_physical_checks_passed"])
  self.assertFalse(z["all_independent_external_physics_backends_connected"])
  self.assertIsNone(z["full_Zee_allowed_or_excluded"])
  self.assertIn("FlavorKit",z["required_validation"])

 def test_model_file_presence_is_not_valid_SARAH_implementation(self):
  with tempfile.TemporaryDirectory() as d:
   model=Path(d)/"Zee";model.mkdir()
   for f in SARAH_FILES:
    (model/f).write_text("(* synthetic, deliberately NOT a physical SARAH model *)\n")
   result=sarah_model_info(model)
   self.assertTrue(result["all_four_source_files_present"])
   self.assertEqual(set(result["source_sha256"]),set(SARAH_FILES))
   self.assertFalse(result["model_validated"])
   z=tool_status(opts(sarah_model_dir=model))
   self.assertTrue(z["prerequisites_detected_NOT_validated"][
     "SARAH_model_full_source_files"])
   self.assertFalse(z["source_model_usable_for_Zee_exclusions"])

 def test_fake_executable_is_only_executable_not_physical_validation(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"SPhenoZee"
   path.write_text("#!/bin/sh\nexit 0\n")
   path.chmod(0o755)
   result=tool_status(opts(spheno_model_executable=path))
   self.assertTrue(result["commands"]["SPheno_Zee"]["executable"])
   self.assertFalse(result["model_compile_and_physical_checks_passed"])
   self.assertIsNone(result["full_Zee_allowed_or_excluded"])

 def test_missing_executable_refused_as_detected(self):
  with tempfile.TemporaryDirectory() as d:
   binary=Path(d)/"BSMArt"
   self.assertFalse(command_info(("BSMArt",),binary)["detected"])
   binary.write_text("not executable\n")
   self.assertFalse(command_info(("BSMArt",),binary)["executable"])

if __name__=="__main__":unittest.main()
