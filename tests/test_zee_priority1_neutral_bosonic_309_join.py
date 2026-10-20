"""N2 original N1 partial-width preservation and fail-closed Bosonic merge."""
import copy,math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_priority1_neutral_bosonic_309_one_shot as W
from zee_priority1_neutral_bosonic_two_body import STATUS as N2_SOURCE

def point():
 return {"id":"B4_N2_TEST","mH1":208.77,"mH2":681.85,
         "mh2":597.72,"ma":635.23,"beta":math.atan(5.647),
         "alpha":math.atan(5.647)+.003,"gamma":1.1201,
         "m12sq":57700.,"lc":4.473,"k1":1.082,
         "k2":.00398,"k12":-.001266}

def n1():
 p={"h":{"e_e":.00001},"H":{"e_e":.00001},
    "A":{"e_e":.00001},"H1":{"tb":.5},"H2":{"H1_Z":3.}}
 return {
  "candidate_id":"B4_N2_TEST",
  "status":"P1_309_NEUTRAL_H_H_A_AND_CHARGED_H1_H2_INCLUDED_TREE_WIDTHS_NOT_COMPLETE",
  "particles_included_LO_GeV":p,
  "included_width_sums_NOT_physical_totals_GeV":{
    k:sum(v.values()) for k,v in p.items()},
  "cascade_proxy_NOT_signal_rate":.59,
 }

class N2OriginalSourceJoin(unittest.TestCase):
 def test_original_N1_five_states_retained_every_mode(self):
  source=n1()
  old=copy.deepcopy(source)
  result=W.merge_one(point(),source)
  self.assertEqual(result["status"],W.STATUS)
  self.assertEqual(set(result["particles_included_LO_GeV"]),
                   {"h","H","A","H1","H2"})
  for state,channels in old["particles_included_LO_GeV"].items():
   for k,v in channels.items():
    self.assertEqual(result["particles_included_LO_GeV"][state][k],v)
   self.assertGreaterEqual(result[
        "included_width_sums_NOT_physical_totals_GeV"][state],
       old["included_width_sums_NOT_physical_totals_GeV"][state])
  self.assertEqual(result["N2_new_neutral_bosonic_GeV"]["H"][
       "H1plus_H1minus"],
      result["particles_included_LO_GeV"]["H"]["H1plus_H1minus"])
  self.assertEqual(result["old_cascade_proxy_NOT_signal_rate"],.59)
  self.assertIsNone(result["complete_Zee_allowed_or_excluded"])
  self.assertFalse(result["all_physical_decay_channels_enumerated"])
  self.assertFalse(result["full_five_state_physical_total_widths_computed"])

 def test_mismatch_original_ID_fails_source_closed(self):
  z=n1();z["candidate_id"]="B4_OTHER"
  with self.assertRaisesRegex(ValueError,"wrong E2 point"):
   W.merge_one(point(),z)

 def test_duplicate_channel_source_fails(self):
  z=n1();z["particles_included_LO_GeV"]["H"][
        "H1plus_H1minus"]=.001
  z["included_width_sums_NOT_physical_totals_GeV"]["H"]+=.001
  with self.assertRaisesRegex(ValueError,"duplicate decay mode"):
   W.merge_one(point(),z)

 def test_negative_N1_partial_detected(self):
  z=n1();z["particles_included_LO_GeV"]["H"]["e_e"]=-.01
  with self.assertRaisesRegex(ValueError,"illegal partial width"):
   W.merge_one(point(),z)

 def test_five_state_incomplete_stays_blocked(self):
  from zee_priority1_contracts import validate_decays
  merged=W.merge_one(point(),n1())
  self.assertEqual(validate_decays(merged,{}),
                   "BLOCKED_DECAY_CHANNEL_COMPLETENESS")

if __name__=="__main__":unittest.main()
