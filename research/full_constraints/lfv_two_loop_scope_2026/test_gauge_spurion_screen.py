import math,unittest
import numpy as np
from research.full_constraints.lfv_two_loop_scope_2026.gauge_spurion_screen import (
 currents,lepton_conserving_spurion_allowed,evaluate,IDS,MEGII
)

class ZeeGaugeSpurionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.x=evaluate()
 def test_charge_and_projectors(self):
  for g in (0,.1,.7,1.0889500926314342,1.3165278528084012,math.pi/2):
   j=currents(g);u,v,p,Q,Z=[j[k] for k in ("u","v","P","Q","Z_over_g_cW")]
   np.testing.assert_allclose(u@v,0,atol=3e-16)
   np.testing.assert_allclose(p@p,p,atol=3e-16)
   np.testing.assert_allclose(p+np.outer(v,v),Q,atol=3e-16)
   np.testing.assert_allclose(Q@Z,Z@Q,atol=3e-16)
   self.assertAlmostEqual(Z[0,1],-.25*math.sin(2*g),places=15)
   self.assertAlmostEqual(np.trace(Z),.5-2*.23129,places=15)
 def test_mixed_charge_kernel_degenerate_and_split(self):
  for g in (.1,.7,1.2):
   u,v=currents(g)["u"],currents(g)["v"]
   for a,b in ((1.,1.),(17.,17.),(3.,90.)):
    self.assertAlmostEqual(float(u@np.diag([a,b])@v),
                           math.sin(g)*math.cos(g)*(a-b),places=12)
 def test_lepton_number_spurion(self):
  for x in range(4):
   for y in range(4):
    self.assertEqual(lepton_conserving_spurion_allowed(x,y),x==y)
  for a,b in ((-1,0),(1.,1),(2,-1)):
   with self.assertRaises(ValueError):lepton_conserving_spurion_allowed(a,b)
  with self.assertRaises(ValueError):currents(float("nan"))
 def test_four_benchmarks_not_global_acceptance(self):
  self.assertEqual(tuple(self.x["cards"]),IDS)
  self.assertIsNone(self.x["global_acceptance"])
  self.assertFalse(self.x["complete_all_two_loop_Zee"])
  self.assertEqual(self.x["physical_lfv"],"UNKNOWN")
  for r in self.x["cards"].values():
   self.assertLess(r["direct_D_e_mu_max"],4e-19)
   self.assertGreater(r["conditional_missing_F_dressing_K_threshold"],4e5)
   self.assertIsNone(r["physical_missing_K_bound"])
   self.assertIsNone(r["complete_Zee_two_loop_K"])
   self.assertEqual(r["MEGII_90CL_BR"],MEGII)
 def test_source_matched_necessary_K_numeric(self):
  expected={"D7_NO":17582382.82909747,"D7_IO":10101276.490189353,
            "F13_NO":703708.137090411,"F13_IO":404791.5830356612}
  for k,target in expected.items():
   ratio=self.x["cards"][k]["conditional_missing_F_dressing_K_threshold"]/target
   self.assertAlmostEqual(ratio,1,places=9)

if __name__=="__main__":unittest.main()
