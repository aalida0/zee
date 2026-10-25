"""N3 actual P1 five-state partial-width export regressions.

Tests real N3 scalar potential calculation, preserves old N2 channels,
requires correctly attributable source + N3 kernel fingerprint and
verifies canonical P1 never evaluates incomplete HiggsBounds inputs.
"""
import copy,json,math,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_priority1_N3_309_one_shot as N
from zee_priority1_contracts import load_export,validate_decays,evaluate

def source():
 p={"id":"B4_N3_SOURCE","mH1":300.,"mH2":700.,
    "mh2":580.7,"ma":633.7,"alpha":1.398,"beta":1.394,
    "gamma":1.089,"m12sq":57700.,"lc":4.473,
    "k1":1.082,"k2":.00398,"k12":-.001266}
 states={"h":{"e_e":.00001,"Z_Z_onshell_tree":0.},
         "H":{"e_e":.00001,"H1plus_H1minus":0.},
         "A":{"e_e":.00001,"H1_W_both_charge_modes":3.5},
         "H1":{"tb":1.},"H2":{"H1_Z":3.0}}
 prev={"candidate_id":p["id"],
       "status":"P1_N2_309_SOURCE_H_H_A_CHARGED_Z_W_AND_CHARGED_PAIRS_NOT_COMPLETE",
       "particles_included_LO_GeV":states,
       "included_width_sums_NOT_physical_totals_GeV":{
          k:sum(v.values()) for k,v in states.items()},
       "old_cascade_proxy_NOT_signal_rate":.59}
 return p,prev

class N3ArchiveContract(unittest.TestCase):
 def test_real_N3_neutral_Hhh_added_to_existing_N2_5states(self):
  p,original=source()
  c=copy.deepcopy(original)
  z=N.merge_one(p,original)
  self.assertEqual(z["status"],N.STATUS)
  self.assertEqual(set(z["particles_included_LO_GeV"]),{"h","H","A","H1","H2"})
  self.assertGreater(z["N3_new_neutral_scalar_pair_LO_GeV"]["H"][
                          "h_h_identical"],0.)
  self.assertAlmostEqual(z["included_width_sums_NOT_physical_totals_GeV"]["H"],
     z["original_N1_included_sums_NOT_physical_totals_GeV"]["H"]
     if "original_N1_included_sums_NOT_physical_totals_GeV" in z
     else (sum(c["particles_included_LO_GeV"]["H"].values())+
           z["N3_new_neutral_scalar_pair_LO_GeV"]["H"]["h_h_identical"]+
           z["N3_new_neutral_scalar_pair_LO_GeV"]["H"]["A_A_identical"]))
  for state,pred in c["particles_included_LO_GeV"].items():
   for k,val in pred.items():
    self.assertEqual(z["particles_included_LO_GeV"][state][k],val)
  self.assertIsNone(z["complete_Zee_allowed_or_excluded"])
  self.assertFalse(z["all_physical_decay_channels_enumerated"])

 def test_id_mismatch_rejected(self):
  p,source_record=source()
  source_record["candidate_id"]="B4_UNRELATED"
  with self.assertRaisesRegex(ValueError,"ID disagreement"):
   N.merge_one(p,source_record)

 def test_duplicate_hh_mode_rejected(self):
  p,prior=source()
  prior["particles_included_LO_GeV"]["H"]["h_h_identical"]=1.
  with self.assertRaisesRegex(ValueError,"duplicate neutral scalar"):
   N.merge_one(p,prior)

 def test_schema_export_load_and_HiggsBounds_blocked(self):
  p,prior=source()
  row=N.merge_one(p,prior)
  payload=N.export_payload([row],{"N2_archive_SHA256":"b"*64})
  self.assertIn("source",payload["provenance"])
  self.assertFalse(payload["provenance"][
      "independent_external_UFO_or_MadWidth_validation_completed"])
  points={p["id"]:{
    "h":125.,"H":p["mh2"],"A":p["ma"],
    "H1":p["mH1"],"H2":p["mH2"]}}
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/"partial.json"
   file.write_text(json.dumps(payload))
   records,proof=load_export(file,"decays",points)
   self.assertEqual(set(records),set(points))
   self.assertIn("N3_neutral_kernel_SHA256",proof)
   self.assertEqual(validate_decays(records[p["id"]],{}),
        "BLOCKED_DECAY_CHANNEL_COMPLETENESS")
   summary=evaluate(points,{"decays":records})
   self.assertEqual(summary[0]["stages"]["decays"],
        "BLOCKED_DECAY_CHANNEL_COMPLETENESS")
   self.assertIsNone(summary[0]["experimental_Zee_allowed_or_excluded"])

 def test_no_fake_all_channels_exclusion(self):
  p,prior=source()
  a=N.merge_one(p,prior)
  self.assertFalse(a["full_five_state_physical_total_widths_computed"])
  self.assertFalse(a["off_shell_and_QCD_treatment_validated"])
  self.assertIsNone(a["independent_width_validation_reference"])
  self.assertIsNone(a["complete_Zee_allowed_or_excluded"])

if __name__=="__main__":unittest.main()
