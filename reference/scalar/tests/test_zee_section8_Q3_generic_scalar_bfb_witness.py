"""Q3 generic complex Zee quartic exact minimization and negative-witness tests."""
import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q3_generic_scalar_bfb_witness import (
 Quartics,quartic,minimize_singlet_exact,exact_single_doublet_necessary,
 portal_matrix_psd,deterministic_counterexamples,coverage_manifest,
 reference_diagnostics)
class TestQ3Quartic(unittest.TestCase):
 def setUp(self):
  self.p=Quartics(.36,.44,.12,-.07,.04+.03j,.08-.01j,-.02+.04j,.19,-.1,.2,.06-.11j)
 def test_inventory(self):
  d=coverage_manifest()
  self.assertEqual(d['source_eq_2_4_generic_Zee_quartic_operators'],15)
  self.assertFalse(any(d['NOT_established'].values()))
 def test_exact_s_minimization(self):
  for x,y,z in ((1.,0.,0j),(.4,.6,.2j),(.3,.7,.4),(.5,.5,.2+.1j)):
   d=minimize_singlet_exact(self.p,x,y,z)
   s=d['optimal_s']
   self.assertAlmostEqual(d['v4_infimum'],quartic(self.p,x,y,z,s),places=12)
   for a in (.01,.1,1.,5.):
    self.assertLessEqual(d['v4_infimum'],quartic(self.p,x,y,z,s+a)+1e-12)
 def test_complex_rephase(self):
  import cmath
  p=self.p;a=.71;x=.7;y=.8;z=.3+.2j;s=.37
  q=Quartics(p.l1,p.l2,p.l3,p.l4,p.l5*cmath.exp(-2j*a),
    p.l6*cmath.exp(-1j*a),p.l7*cmath.exp(-1j*a),
    p.lh,p.l8,p.l9,p.l10*cmath.exp(-1j*a))
  self.assertAlmostEqual(quartic(p,x,y,z,s),
                         quartic(q,x,y,z*cmath.exp(1j*a),s),places=12)
 def test_gram_constraints(self):
  for x,y,z,s in ((1.,1.,2j,0.),(0.,1.,.1,0.),(1.,1.,0.,-1.)):
   with self.assertRaises(ValueError):quartic(self.p,x,y,z,s)
 def test_copositivity_boundary(self):
  a=Quartics(1.,1.,1.,0,0,0,0,1.,-math.sqrt(2),0,0)
  b=Quartics(1.,1.,1.,0,0,0,0,1.,-1.5,0,0)
  self.assertTrue(exact_single_doublet_necessary(a)['H1_singlet'])
  self.assertFalse(exact_single_doublet_necessary(b)['H1_singlet'])
  self.assertLess(minimize_singlet_exact(b,1.,0.,0.)['v4_infimum'],0.)
 def test_singlet_runaway(self):
  p=Quartics(1.,1.,0,0,0,0,0,0.,-1.,0.,0.)
  self.assertTrue(minimize_singlet_exact(p,1.,0.,0.)['singlet_runaway'])
 def test_portal_matrix(self):
  p=Quartics(1.,1.,0,0,0,0,0,1.,.25,.36,.3j)
  q=Quartics(1.,1.,0,0,0,0,0,1.,.25,.36,.31j)
  self.assertTrue(portal_matrix_psd(p));self.assertFalse(portal_matrix_psd(q))
 def test_negative_witness_substitution(self):
  p=Quartics(.26,.4,.1,.05,0,0,0,.2,-1.,.2,0)
  d=deterministic_counterexamples(p);w=d['negative_witness']
  self.assertIsNotNone(w)
  self.assertLess(quartic(p,w['x'],w['y'],complex(w['z_re'],w['z_im']),w['s']),0.)
  self.assertFalse(d['absence_proves_BFB'])
 def test_complex_portal_instability(self):
  p=Quartics(1.,1.,0,0,0,0,0,.1,1.,1.,-2.)
  self.assertIsNotNone(deterministic_counterexamples(p)['negative_witness'])
 def test_reference_is_synthetic(self):
  d=reference_diagnostics()
  self.assertFalse(d['full_UV_Zee_betas_available'])
  self.assertIsNone(d['physical_Zee_allowed'])
  self.assertIsNone(d['synthetic_stable_example_no_negative_witness']['negative_witness'])
  self.assertIsNotNone(d['synthetic_unstable_example_has_negative_witness']['negative_witness'])
if __name__=='__main__':unittest.main()
