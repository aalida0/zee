"""Numerical physics regressions for NO/IO Takagi and LFV interference."""
import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import numpy as np
import zee_priority1_neutrino_gaussian as n
import zee_priority1_coherent_lfv as lf

def pmns(th12=.59,th23=.85,th13=.15,delta=1.2):
 c12,c23,c13=np.cos([th12,th23,th13]);s12,s23,s13=np.sin([th12,th23,th13])
 return np.array([
 [c12*c13,s12*c13,s13*np.exp(-1j*delta)],
 [-s12*c23-c12*s23*s13*np.exp(1j*delta),
  c12*c23-s12*s23*s13*np.exp(1j*delta),s23*c13],
 [s12*s23-c12*c23*s13*np.exp(1j*delta),
  -c12*s23-s12*c23*s13*np.exp(1j*delta),c23*c13]],complex)

def matrix(order):
 masses=[.01,.013,.051] if order=="NO" else [.052,.0527,.01]
 U=pmns()
 return U.conj()@np.diag(masses)@U.conj().T

def osc_ref(p):
 scales=np.array([.02,.01,.03,.00002,.0002])
 return {"ordering":p["ordering"],"data_release":"SYNTHETIC_TEST_NO_EXP_REFERENCE",
         "fields":list(n.FIELDS),
         "central":[p[q] for q in n.FIELDS],
         "covariance":np.diag(scales**2).tolist()}

class TestActualNumericalComponents(unittest.TestCase):
 def test_Takagi_NO_exact_mass_matrix_reconstruction(self):
  M=matrix("NO")
  masses,U=n.takagi(M,"NO")
  self.assertLess(np.max(abs(U.conj()@np.diag(masses)@U.conj().T-M)),1e-10)
  self.assertTrue(masses[0]<masses[1]<masses[2])
  self.assertAlmostEqual(masses[2],.051,places=8)

 def test_Takagi_IO_exact_mass_matrix_reconstruction(self):
  M=matrix("IO")
  masses,U=n.takagi(M,"IO")
  self.assertLess(np.max(abs(U.conj()@np.diag(masses)@U.conj().T-M)),1e-10)
  self.assertAlmostEqual(masses[2],.01,places=8)
  self.assertLess(masses[2],masses[0])

 def test_PMNS_angles_CP_and_mass_splittings(self):
  p=n.parameters(matrix("NO"),"NO")
  self.assertAlmostEqual(p["s12_sq"],math.sin(.59)**2,places=9)
  self.assertAlmostEqual(p["s13_sq"],math.sin(.15)**2,places=9)
  self.assertAlmostEqual(p["s23_sq"],math.sin(.85)**2,places=9)
  self.assertAlmostEqual(p["delta_CP_rad"],1.2,places=9)
  self.assertAlmostEqual(p["dm21_sq_eV2"],.013**2-.01**2,places=10)

 def test_massless_lightest_Majorana_neutrino_supported(self):
  U=pmns()
  for ordering,masses in (("NO",[0.,.0086,.05]),
                           ("IO",[.05,.0508,0.])):
   M=U.conj()@np.diag(masses)@U.conj().T
   out=n.parameters(M,ordering)
   self.assertAlmostEqual(min(out["masses_eV"]),0.,places=8)
   self.assertAlmostEqual(out["s13_sq"],math.sin(.15)**2,places=8)

 def test_unphysical_Majorana_column_phases_do_not_change_PMNS_angles(self):
  U=pmns()
  m=np.asarray([.01,.013,.051])
  x=U.conj()@np.diag(m)@U.conj().T
  V=U@np.diag(np.exp(1j*np.array([.3,1.2,2.1])))
  y=V.conj()@np.diag(m)@V.conj().T
  a=n.parameters(x,"NO"); bb=n.parameters(y,"NO")
  for key in ("s12_sq","s13_sq","s23_sq","delta_CP_rad"):
   self.assertAlmostEqual(a[key],bb[key],places=8)

 def test_reference_covariance_gaussian_proxy_chi2(self):
  p=n.parameters(matrix("IO"),"IO")
  ref=osc_ref(p)
  out=n.gaussian_fit(p,ref)
  self.assertLess(out["chi2_Gaussian_NOT_NuFIT_likelihood"],1e-16)
  self.assertIsNone(out["experimental_CL_exclusion"])
  ref["covariance"][0][0]=-1
  with self.assertRaisesRegex(ValueError,"positive definite"):
   n.gaussian_fit(p,ref)

 def test_symmetric_neutrino_input_required(self):
  bad=np.eye(3,dtype=complex)
  bad[0,1]=.3j
  with self.assertRaisesRegex(ValueError,"symmetric"):
   n.takagi(bad,"NO")
  with self.assertRaisesRegex(ValueError,"ordering"):
   n.takagi(matrix("NO"),"UNKNOWN")

 def test_both_orderings_report_without_model_exclusion(self):
  M=matrix("NO")
  ref={k:osc_ref(n.parameters(M,k)) for k in ("NO","IO")}
  z=n.evaluate(M,ref)
  self.assertEqual(set(z["orderings"]),{"NO","IO"})
  self.assertFalse(z["full_global_oscillation_likelihood_computed"])
  self.assertIsNone(z["allowed_or_excluded"])
 
 def test_LFV_two_diagrams_interfere_before_square(self):
  z=lf.coherent_dipole({
    "one_loop_neutral":{"CL_GeV_minus2":[1e-10,0.],
                        "CR_GeV_minus2":[0,0]},
    "two_loop_Barr_Zee_fermion":{"CL_GeV_minus2":[-1e-10,0.],
                                  "CR_GeV_minus2":[0,0]}},
    norm_br=1)
  self.assertAlmostEqual(z["BR_coherent_amplitude_sum"],0.,places=16)
  self.assertGreater(sum(z["individual_BR_if_alone_NOT_ADDITIVE"].values()),0.)
  self.assertLess(z["interference_term_BR"],0.)
  self.assertFalse(z["full_radiative_LFV_rate_certified"])
  self.assertIsNone(z["Zee_allowed_or_excluded"])

 def test_LFV_complete_six_topology_flag_and_common_convention(self):
  amplitudes={q:{"CL_GeV_minus2":[1e-12,0],
                 "CR_GeV_minus2":[0,0]} for q in lf.PARTS}
  z=lf.coherent_dipole(amplitudes,1.,
      all_diagrams_verified=True,common_operator_convention=True)
  self.assertTrue(z["full_radiative_LFV_rate_certified"])
  self.assertFalse(z["full_Zee_LFV_likelihood_evaluated"])
  r=lf.coherent_dipole(amplitudes,1.,
      all_diagrams_verified=False,common_operator_convention=True)
  self.assertFalse(r["full_radiative_LFV_rate_certified"])
  with self.assertRaisesRegex(ValueError,"Unknown"):
   lf.coherent_dipole({"magic":{}},1.)

if __name__=="__main__":unittest.main()
