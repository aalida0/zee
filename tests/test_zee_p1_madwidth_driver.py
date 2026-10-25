"""MadWidth actual process deck, complete SLHA DECAY table parsing, fail-closed source."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import zee_p1_madwidth_driver as D
from test_zee_p1_ufo_model_audit import model

def valid():
 return """BLOCK MASS
 25 125
 225 599
 226 633
 227 680
 228 210
DECAY 25 4.0E-3
 1.0 2 5 -5
DECAY 225 1.0E+1
 5.0E-1 2 25 25
 5.0E-1 2 6 -6
DECAY 226 1.0E+1
 1.0 2 24 228
DECAY 227 1.0E+1
 6.5E-1 2 23 228
 3.5E-1 2 6 -5
DECAY 228 1.0E+0
 1.0 2 6 -5
"""

class MadWidthSource(unittest.TestCase):
 def test_actual_SLHA_all_five_widths_and_partial_rates(self):
  with tempfile.TemporaryDirectory() as d:
   card=Path(d)/"after_madwidth.slha"
   card.write_text(valid())
   tables=D.parse_widths(card)
   self.assertEqual(set(D.PDGS),set(tables)&set(D.PDGS))
   self.assertAlmostEqual(tables[225]["total_width_GeV"],10.)
   self.assertAlmostEqual(tables[227]["modes"][0]["partial_width_GeV"],6.5)
   self.assertEqual(tables[228]["modes"][0]["daughters"],(6,-5))

 def test_missing_heavy_charged_table_hard_failure(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/"card"
   file.write_text(valid().replace("DECAY 227 1.0E+1",
                                    "DECAY 999 1.0E+1"))
   with self.assertRaisesRegex(ValueError,"did not compute scalar PDG 227"):
    D.parse_widths(file)

 def test_wrong_branching_closure_does_not_pass(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/"card"
   file.write_text(valid().replace(
      " 3.5E-1 2 6 -5"," 1.0E-1 2 6 -5"))
   with self.assertRaisesRegex(ValueError,"Incomplete MadWidth"):
    D.parse_widths(file)

 def test_negative_total_or_partial_refused(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/"card"
   file.write_text(valid().replace("DECAY 228 1.0E+0",
                                 "DECAY 228 -1.0E+0"))
   with self.assertRaisesRegex(ValueError,"invalid SLHA"):
    D.parse_widths(file)
   file.write_text(valid().replace(" 1.0 2 6 -5",
                                    " -0.1 2 6 -5"))
   with self.assertRaisesRegex(ValueError,"Invalid MadWidth branching"):
    D.parse_widths(file)

 def test_mg5_model_import_and_two_three_body_deck(self):
  # Keep temporary physical source under /home to match actual AF policy.
  base=Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory(dir=base) as d:
   root=Path(d)
   ufo=model(root/"Zee_UFO_complex")
   card=root/"physically_unmatched_param_card.dat"
   card.write_text("BLOCK MASS\n 25 125\n")
   out=root/"actual_madwidth_task"
   deck,audit=D.make_deck(ufo,card,out)
   self.assertIn("import model "+str(ufo),deck)
   self.assertIn("--body_decay=3",deck)
   self.assertIn("compute_widths 25 225 226 227 228",deck)
   self.assertTrue(audit["static_necessary_conditions_pass"])
   self.assertFalse(audit["valid_Zee_MadWidth_309_input_ready"])
   report=D.run(ufo,card,out)
   self.assertFalse(report["MadWidth_executed"])
   manifest=json.loads((out/"manifest.json").read_text())
   self.assertFalse(manifest["physics_five_state_complete"])
   self.assertIsNone(manifest["model_allowed_or_excluded"])
   with self.assertRaisesRegex(ValueError,"Never overwrite"):
    D.make_deck(ufo,card,out)

 def test_real_only_ufo_refused_for_complex_E3(self):
  base=Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory(dir=base) as d:
   root=Path(d);ufo=model(root/"original",complex_flavor=False)
   card=root/"card.dat";card.write_text("BLOCK MASS\n")
   with self.assertRaisesRegex(ValueError,"incomplete vertices or real-only flavor"):
    D.make_deck(ufo,card,root/"output")

if __name__=="__main__":unittest.main()
