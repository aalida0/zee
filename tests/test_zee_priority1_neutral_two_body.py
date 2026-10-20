"""Numerical neutral Zee leptonic + quark-ansatz/vector LO regressions.

Independent analytic mass-threshold/mixing tests and cross-stage h125
D5 source closure. These are real two-body partial widths only.
"""
import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_priority1_neutral_two_body as N
import zee_priority1_neutral_309_one_shot as W
from gateA1b_hierarchical_no_seed import (
 target_neutrino_matrix,antisymmetric_f_with_null_condition,
 solve_lepton_yukawa)
from gateB3_general_zee_charged_lepton_widths import evaluate as charged_eval
from zee_gateD5_h125_direct_LFV_27 import exact_diagonal_width
from gateA1d_neutral_tree_lfv import scalar_couplings

def point():
 return {"id":"B4_TEST","mh2":590.,"ma":630.,"mH1":300.,
         "mH2":700.,"alpha":1.398,"beta":1.394,
         "gamma":1.089,"m12sq":57700.,
         "lc":4.473,"k1":1.082,"k2":.00398,"k12":-.001266}
def solution():
 m,_=target_neutrino_matrix()
 f,_=antisymmetric_f_with_null_condition(m)
 Y,rank,_=solve_lepton_yukawa(f,m)
 assert rank==5
 return m,f,Y

class NeutralPartialPhysics(unittest.TestCase):
 def test_source_optimized_like_Y_all_3_neutral_state_finite(self):
  _,_,Y=solution()
  report=N.calculate(point(),Y)
  self.assertEqual(report["status"],N.STATUS)
  self.assertTrue(report["h125_three_LFV_rates_exact_D5_reference_closure"])
  self.assertEqual(set(report["tree_level_included_modes_GeV"]),{"h","H","A"})
  self.assertTrue(all(len(ch)==12 for ch in report[
      "tree_level_included_modes_GeV"].values()))
  for state,pred in report["tree_level_included_modes_GeV"].items():
   self.assertTrue(all(v>=0 and math.isfinite(v) for v in pred.values()))
   self.assertAlmostEqual(sum(pred.values()),report[
       "included_width_sums_NOT_physical_total_GeV"][state],places=10)
  self.assertFalse(report["complete_physical_neutral_totals_computed"])
  self.assertIsNone(report["experimental_Zee_allowed_or_excluded"])

 def test_complex_diagonal_vs_source_for_scalar_pseudoscalar(self):
  _,_,Y=solution()
  p=point()
  z=N.calculate(p,Y)
  matrices=N.scalar_couplings(Y,mh=125.,mH=p["mh2"],
      mA=p["ma"],alpha=p["alpha"],beta=p["beta"])
  for key,(C,mass) in zip(N.NEUTRAL,matrices):
   for i,lepton in enumerate(N.LEPTONS):
    self.assertAlmostEqual(z["tree_level_included_modes_GeV"][key][
       lepton+"_"+lepton],
       exact_diagonal_width(C,mh=mass,i=i),places=12)
  self.assertEqual(z["tree_level_included_modes_GeV"]["A"]["W_W_onshell_tree"],0.)
  self.assertEqual(z["tree_level_included_modes_GeV"]["A"]["Z_Z_onshell_tree"],0.)

 def test_alpha_equal_beta_h_is_sm_lepton_diagonal(self):
  Y=np.array([[.05,.001j,0.],[-.001,0.2,0.],[0.,0.,.6]],dtype=complex)
  p=point();p["alpha"]=p["beta"]
  report=N.calculate(p,Y)
  self.assertEqual(report["tree_level_included_modes_GeV"]["h"][
      "e_mu_both_charges"],0.)
  self.assertEqual(report["tree_level_included_modes_GeV"]["h"][
      "e_tau_both_charges"],0.)
  self.assertEqual(report["tree_level_included_modes_GeV"]["h"][
      "mu_tau_both_charges"],0.)
  for lepton,c in zip(N.LEPTONS,N.LEPTON_MASSES):
   expected=N.quark_two_body(125.,c,c/N.VEV,"even")/3.
   # quark_two_body has Nc=3, while leptons have Nc=1
   self.assertAlmostEqual(report["tree_level_included_modes_GeV"]["h"][
        lepton+"_"+lepton],expected,places=13)

 def test_quark_CP_threshold_and_fixed_mass_beta_powers(self):
  self.assertEqual(N.quark_two_body(300.,172.,1.,"even"),0.)
  M,m=700.,172.
  scalar=N.quark_two_body(M,m,1.,"even")
  pseudo=N.quark_two_body(M,m,1.,"odd")
  beta=math.sqrt(1-4*(m/M)**2)
  self.assertAlmostEqual(scalar/pseudo,beta*beta,places=13)
  self.assertGreater(pseudo,scalar)
  self.assertAlmostEqual(N.quark_two_body(M,m,0.,"odd"),0.)

 def test_vector_threshold_SM_normalization_and_alignment(self):
  self.assertEqual(N.on_shell_vector_two_body(125.,N.MW,1.,2),0.)
  self.assertEqual(N.on_shell_vector_two_body(125.,N.MZ,1.,1),0.)
  self.assertGreater(N.on_shell_vector_two_body(590.,N.MW,1.,2),0.)
  mix=N.kappas(1.39,1.39)
  self.assertAlmostEqual(mix["h"]["V"],1.)
  self.assertAlmostEqual(mix["h"]["up"],1.)
  self.assertAlmostEqual(mix["h"]["down"],1.)
  self.assertEqual(mix["H"]["V"],0.)
  self.assertEqual(mix["A"]["V"],0.)
  self.assertAlmostEqual(mix["H"]["up"],1/math.tan(1.39))
  self.assertAlmostEqual(mix["H"]["down"],-math.tan(1.39))

 def test_strict_bad_Y_and_beta_rejection(self):
  with self.assertRaisesRegex(ValueError,"Require complex"):
   N.calculate(point(),np.ones((2,3)))
  with self.assertRaisesRegex(ValueError,"non-singular"):
   N.kappas(0.,1.)
  with self.assertRaisesRegex(ValueError,"neutral mass"):
   N.calculate({**point(),"ma":-1.},np.zeros((3,3),complex))

 def test_source_B3_charged_vs_new_N1_neutral_charged_join(self):
  M,f,Y=solution();p=point()
  charged=charged_eval(p,f,Y,M)
  obj={"candidate_id":p["id"],
       "charged_included_LO_GeV":charged["partial_widths_included_GeV"],
       "charged_included_totals_NOT_physical_total_GeV":
          charged["totals_included_GeV"],
       "conditional_H2_H1Z_fraction_in_included_channels_ONLY":
          charged["BR_H2_H1Z_included_general_Zee"],
       "conditional_H1_tb_fraction_in_included_channels_ONLY":
          charged["BR_H1_tb_included_general_Zee"],
       "conditional_production_weighted_cascade_proxy_NOT_rate":
          charged["production_weighted_partial_cascade_proxy"]}
  Yobj={"candidate_id":p["id"],
        "diagnostic_status":"MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED",
        "D2":{"chosen_optimized_source":{"solution":{
          "candidate_id":p["id"],
          "Y":{"real":Y.real.tolist(),"imag":Y.imag.tolist()}}}}}
  z=W.join_one(p,Yobj,obj)
  self.assertEqual(set(z["particles_included_LO_GeV"]),{"h","H","A","H1","H2"})
  self.assertTrue(z["h125_LFV_exact_source_D5_reproduced"])
  self.assertFalse(z["all_physical_decay_channels_enumerated"])
  self.assertIsNone(z["complete_Zee_allowed_or_excluded"])
  self.assertAlmostEqual(z["cascade_proxy_NOT_signal_rate"],charged[
      "production_weighted_partial_cascade_proxy"],places=12)

if __name__=="__main__":unittest.main()
