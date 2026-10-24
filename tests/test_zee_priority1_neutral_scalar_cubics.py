"""N3 exact neutral scalar cubic source and independent potential tests."""
import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_priority1_neutral_scalar_cubics as N
from gate6_width_inventory import scalar_width

def point(**kwargs):
 p={"id":"B4_N3_TEST","mH1":300.,"mH2":700.,
   "mh2":580.7,"ma":633.7,"alpha":1.398,
   "beta":1.394,"gamma":1.089,"m12sq":57700.,
   "lc":4.473,"k1":1.082,"k2":.00398,"k12":-.001266}
 return {**p,**kwargs}

class N3Cubic(unittest.TestCase):
 def test_actual_Gate6_Hhh_AA_tree_potential(self):
  p=point()
  z=N.calculate(p)
  self.assertEqual(z["status"],N.STATUS)
  self.assertTrue(z["CP_even_and_CP_odd_masses_source_closed"])
  self.assertTrue(z["potential_independent_finite_difference_closed"])
  self.assertGreater(z["neutral_scalar_pair_included_two_body_GeV"]["H"]["h_h_identical"],0.)
  self.assertEqual(z["neutral_scalar_pair_included_two_body_GeV"]["H"]["A_A_identical"],0.)
  self.assertEqual(z["neutral_scalar_pair_included_two_body_GeV"]["h"]["A_A_identical"],0.)
  self.assertFalse(z["all_scalar_pair_modes_complete"])
  self.assertIsNone(z["physical_five_state_total_widths"])
  self.assertIsNone(z["experimental_Zee_allowed_or_excluded"])

 def test_all_three_weak_tensor_cubic_crosscheck_independent_potential(self):
  p=N.reconstruct(point())
  t=N.neutral_tensor(p)
  for field,left,b,sector in (
     ("H_h_h",t["H_rotation"],t["h_rotation"],"rho"),
     ("H_A_A",t["H_rotation"],t["A_rotation"],"eta"),
     ("h_A_A",t["h_rotation"],t["A_rotation"],"eta")):
   numeric=N.third_numeric(p,left,b,sector,step=2.)
   self.assertAlmostEqual(
     numeric/t[field] if t[field] else 1.,
     1.,places=5,msg=field)
  self.assertAlmostEqual(float(t["h_rotation"]@t["H_rotation"]),0.,places=14)
  self.assertAlmostEqual(float(t["A_rotation"]@t["A_rotation"]),1.,places=14)

 def test_exact_mass_hessians_follow_gate6(self):
  for args in (
       point(),
       point(alpha=1.22,beta=1.32,gamma=.77,mH1=250.,mH2=725.,
             mh2=675.,ma=820.,m12sq=50000.),
       point(alpha=.82,beta=1.41,gamma=.5,mH1=340.,mH2=830.,
             mh2=720.,ma=740.,m12sq=40000.),
      ):
   obj=N.reconstruct(args)
   z=N.hessian_checks(obj)
   self.assertTrue(z["CP_even_and_CP_odd_masses_source_closed"])
   self.assertAlmostEqual(z["Goldstone_CP_odd_mass2_GeV2"],0.,places=8)
   actual=N.calculate(args)
   self.assertEqual(actual["status"],N.STATUS)

 def test_identical_neutral_factor_two_relative_to_distinct_width(self):
  z=N.calculate(point())
  M=point()["mh2"];mh=125.
  g=z["cubic_couplings_GeV"]["H_h_h"]
  self.assertAlmostEqual(z["neutral_scalar_pair_included_two_body_GeV"]
                        ["H"]["h_h_identical"],
                         .5*scalar_width(M,mh,mh,g),places=11)

 def test_HAA_above_and_below_threshold(self):
  low=point(mh2=500.,ma=400.,mH2=710.)
  self.assertEqual(N.calculate(low)["neutral_scalar_pair_included_two_body_GeV"]
                   ["H"]["A_A_identical"],0.)
  high=point(mh2=980.,ma=370.,mH2=1050.)
  z=N.calculate(high)
  self.assertGreater(z["neutral_scalar_pair_included_two_body_GeV"]["H"]
                     ["A_A_identical"],0.)
  self.assertEqual(z["neutral_scalar_pair_included_two_body_GeV"]["h"]
                   ["A_A_identical"],0.)

 def test_zero_mixing_neutral_cross_tensors_symmetries(self):
  z=N.neutral_tensor(N.reconstruct(point()))
  self.assertTrue(np.allclose(z["full_CP_even_tensor"],
                              z["full_CP_even_tensor"].transpose(1,0,2)))
  self.assertTrue(np.allclose(z["rho_eta_eta_tensor"],
                              z["rho_eta_eta_tensor"].transpose(0,2,1)))
  self.assertEqual(z["full_CP_even_tensor"].shape,(2,2,2))

 def test_invalid_source_input_and_finite_difference(self):
  with self.assertRaisesRegex(ValueError,"missing original scalar"):
   N.calculate({"id":"missing"})
  with self.assertRaisesRegex(ValueError,"finite difference must be positive"):
   N.third_numeric(N.reconstruct(point()),[1,0],[1,0],"rho",-1.)
  with self.assertRaisesRegex(ValueError,"rho/eta must"):
   N.potential(N.reconstruct(point()),[0,0,0],[0,0])

if __name__=="__main__":unittest.main()
