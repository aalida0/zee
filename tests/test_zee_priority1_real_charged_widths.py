"""Real E3->B3 source physics integration (requires NumPy/SciPy).

Crosses genuine existing Zee neutrino algebra and general charged lepton
widths; the scalar B3 and Gate6 source formulas are not replaced by mocks.
No modern flavor/collider exclusion is asserted.
"""
import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1b_hierarchical_no_seed import (
 target_neutrino_matrix,antisymmetric_f_with_null_condition,
 solve_lepton_yukawa)
from gateB3_general_zee_charged_lepton_widths import evaluate
from zee_priority1_charged_width_export import calculate

class TestActualChargedWidths(unittest.TestCase):
 def test_exact_E3_like_fY_backed_B3_widths_and_neutrino_closure(self):
  point={"id":"B4_REAL_SOURCE_KERNEL","mH1":300.,"mH2":700.,
         "mh2":580.7,"ma":633.7,"beta":1.394,
         "alpha":1.398,"gamma":1.089,"m12sq":57700.,
         "lc":4.473,"k1":1.082,"k2":.00398,
         "k12":-.001266}
  target,_=target_neutrino_matrix()
  f,_=antisymmetric_f_with_null_condition(target)
  Y,rank,_=solve_lepton_yukawa(f,target)
  self.assertEqual(rank,5)
  encode=lambda z:{"real":z.real.tolist(),"imag":z.imag.tolist()}
  e3={"candidate_id":point["id"],"full_Zee_allowed_or_excluded":None,
      "diagnostic_status":
         "MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED",
      "D2":{"chosen_optimized_source":{"solution":{
         "candidate_id":point["id"],"f":encode(f),"Y":encode(Y)}}}}
  got=calculate(point,e3)
  raw=evaluate(point,f,Y,target)
  self.assertEqual(got["status"],
       "P1_E3_SOURCE_CLOSED_B3_GENERAL_ZEE_CHARGED_PARTIAL_WIDTHS_NOT_HIGGSBOUNDS")
  self.assertLess(got["B3_selected_neutrino_closure_eV"],1e-9)
  for pid in ("H1","H2"):
   self.assertAlmostEqual(
      got["charged_included_totals_NOT_physical_total_GeV"][pid],
      raw["totals_included_GeV"][pid],places=9)
   self.assertNotIn("tau_nu_TypeII",got["charged_included_LO_GeV"][pid])
   self.assertGreater(got["charged_included_LO_GeV"][pid][
                      "tau_nu_generalZee"],0)
   for mode,v in raw["partial_widths_included_GeV"][pid].items():
    self.assertAlmostEqual(got["charged_included_LO_GeV"][pid][mode],v,places=9)
  self.assertFalse(got["complete_five_state_physical_widths_computed"])
  self.assertFalse(got["all_physical_decay_channels_enumerated"])
  self.assertIsNone(got["experimentally_allowed_or_excluded"])
  self.assertAlmostEqual(got[
       "conditional_production_weighted_cascade_proxy_NOT_rate"],
       math.sin(point["gamma"])**2*
          got["conditional_H2_H1Z_fraction_in_included_channels_ONLY"]*
          got["conditional_H1_tb_fraction_in_included_channels_ONLY"])

if __name__=="__main__":unittest.main()
