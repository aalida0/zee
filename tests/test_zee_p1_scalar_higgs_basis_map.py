"""Exact original Zee 2VEV->Yang/Wu Higgs basis fields, quartics, portals."""
import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_p1_scalar_higgs_basis_map import (
 map_point,check_quartic,invariant_potential,STATUS)

def point(**kwargs):
 p={"id":"B4_REAL_SCALAR_BASIS_TEST",
    "mH1":300.,"mH2":700.,"mh2":580.7,
    "ma":633.7,"alpha":1.398,"beta":1.394,
    "gamma":1.089,"m12sq":57700.,
    "lc":4.473,"k1":1.082,"k2":.00398,"k12":-.001266}
 return {**p,**kwargs}

class HiggsBasisScalar(unittest.TestCase):
 def test_original_Gate6_to_YangWu_all_11_quartics_and_portals(self):
  z=check_quartic(point(),trial_count=100)
  self.assertEqual(z["status"],STATUS)
  self.assertLess(z["quartic_max_relative_residual"],1e-12)
  self.assertTrue(z["internal_mass_and_mu4_muzee_closed"])
  self.assertFalse(z["complete_UFO_lepton_Y_fermion_boson_amplitude_matching"])
  self.assertIsNone(z["complete_Gauge_and_HiggsTools_model_allowed"])
  self.assertEqual(set(z["YangWu_external"]),{
   "lam2","lam3","lam7","lam8","lam9","lam10","lameta"})

 def test_many_independent_physical_mass_mixing_scans(self):
  for i in range(20):
   beta=.6+.035*i
   par=point(beta=beta,alpha=beta+.006*(i-10),
       gamma=.15+.064*i,mH1=210.+9*i,mH2=700.+17*i,
       mh2=520.+13*i,ma=610.+9*i,
       m12sq=41000.+1000*i,
       lc=.2+.2*i,k1=.2+.01*i,k2=.7-.008*i,
       k12=.08-.004*i)
   z=check_quartic(par,trial_count=12,seed=123+i)
   self.assertTrue(z["internal_mass_and_mu4_muzee_closed"])
   self.assertLess(z["quartic_max_relative_residual"],1e-11)

 def test_doublet_rotation_maintains_exact_complex_potential(self):
  par=point()
  z=map_point(par)
  self.assertAlmostEqual(z["YangWu_input_ZEEINPUTS"]["alphabeta"],
      par["alpha"]-par["beta"],places=14)
  self.assertAlmostEqual(z["YangWu_input_ZEEINPUTS"]["phi"],
      math.pi/2-par["gamma"],places=14)
  self.assertEqual(z["higgs_basis"]["lameta"],par["lc"])
  self.assertFalse(z["full_flavor_Y_f_amplitudes_matched"])

 def test_aligned_beta_map_has_source_lam6_zero(self):
  p=point(alpha=1.394,beta=1.394)
  z=map_point(p)
  self.assertAlmostEqual(z["higgs_basis"]["lam6"],0.,places=10)
  self.assertAlmostEqual(z["YangWu_input_ZEEINPUTS"]["alphabeta"],0.,places=14)

 def test_reject_bad_scalar_source_parameters(self):
  with self.assertRaises(ValueError):
   map_point(point(mH2=-200.))
  with self.assertRaises(ValueError):
   invariant_potential([0,0,0],[1,0],0.,{},"two_vev")
  with self.assertRaisesRegex(ValueError,"Unknown scalar basis"):
   invariant_potential([0,0],[0,0],0.,{},"invalid")

if __name__=="__main__":unittest.main()
