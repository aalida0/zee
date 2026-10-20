"""Verify exact archived E2/E3 model origin before real B3 widths."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_priority1_charged_width_export import verify_e2_e3_same_source
from zee_priority1_real_309_one_shot import locate,E2_FILE,SOURCE_E3
from zee_priority1_contracts import hashfile

def fake_pair(root,n=1):
 root=Path(root)
 e2=root/f"E2_campaign_{n}";e3=root/f"E3_campaign_{n}"
 e2.mkdir();e3.mkdir()
 csv=e2/E2_FILE
 csv.write_text("id,mH1,mH2\nB4_0004143,209,681\n")
 e2summary={
   "no_deeper_tree_vacuum_witness_found":309,
   "global_tree_vacuum_certified":False,
   "full_Zee_experimental_allowed_or_excluded":None,
   "output_SHA256":{E2_FILE:hashfile(csv)}}
 (e2/"summary.json").write_text(json.dumps(e2summary))
 file=e3/SOURCE_E3
 file.write_text('{"candidate_id":"B4_0004143"}\n')
 e3summary={"E2_provenance":{
     "E2_summary_SHA256":hashfile(e2/"summary.json"),
     "E2_inputs_sha256":{E2_FILE:hashfile(csv)} }}
 (e3/"summary.json").write_text(json.dumps(e3summary))
 return csv,file

class P1E2E3Provenance(unittest.TestCase):
 def test_exact_archived_E2_E3_sha_link(self):
  with tempfile.TemporaryDirectory() as d:
   e2,e3=fake_pair(d)
   z=verify_e2_e3_same_source(e2,e3)
   self.assertTrue(z["E3_original_E2_SHA_verified"])
   self.assertEqual(z["E2_309_CSV_SHA256"],hashfile(e2))
   self.assertEqual(locate(Path(d)),(e2,e3))

 def test_changed_E2_point_refuses_E3_saved_Yukawas(self):
  with tempfile.TemporaryDirectory() as d:
   e2,e3=fake_pair(d)
   e2.write_text(e2.read_text().replace("209,681","210,682"))
   with self.assertRaisesRegex(ValueError,"SHA/potential provenance mismatch"):
    verify_e2_e3_same_source(e2,e3)
   with self.assertRaisesRegex(ValueError,"Need precisely one E2/E3"):
    locate(Path(d))

 def test_changed_e2_summary_refuses(self):
  with tempfile.TemporaryDirectory() as d:
   e2,e3=fake_pair(d)
   s=e2.parent/"summary.json"
   v=json.loads(s.read_text());v["global_tree_vacuum_certified"]=True
   s.write_text(json.dumps(v))
   with self.assertRaisesRegex(ValueError,"SHA/potential"):
    verify_e2_e3_same_source(e2,e3)

 def test_too_many_complete_archive_copies_must_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   fake_pair(d,1)
   fake_pair(d,2)
   with self.assertRaisesRegex(ValueError,"found 2"):
    locate(Path(d))

 def test_candidate_file_must_be_genuine_E2_named(self):
  with tempfile.TemporaryDirectory() as d:
   e2,e3=fake_pair(d)
   other=e2.with_name("not_original_E2.csv")
   other.write_text(e2.read_text())
   with self.assertRaisesRegex(ValueError,"SHA/potential"):
    verify_e2_e3_same_source(other,e3)

if __name__=="__main__":unittest.main()
