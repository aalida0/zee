"""Independent scalar quartic one-loop Hessian projection regression tests.

These DO NOT constitute AF comparison with genuine PyR@TE output.
"""
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_independent_scalar_hessian_gate import (
    COMPONENTS, PHYSICAL_QUARTICS, A, invariant_matrices, invariants,
    tensor_for_quartics, components_to_couplings, couplings_to_components,
    potential, hessian, scalar_loop_polynomial, quartic_projection,
    independent_scalar_beta, compare_pyrate_scalar_betas, synthetic_quartics,
)

class TestIndependentScalarHessian(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rng=np.random.default_rng(20261020)
        cls.fields=cls.rng.normal(size=(96,10))
        cls.design=quartic_projection(cls.fields)

    def test_field_content_and_projected_operator_rank(self):
        self.assertEqual(A.shape,(5,10,10))
        self.assertEqual(len(COMPONENTS),15)
        self.assertEqual(self.design[0].shape,(96,15))
        self.assertLess(self.design[1],1e5)

    def test_invariants_match_complex_doublets(self):
        r=np.arange(1,11,dtype=float)/11
        p1=np.array([r[0]+1j*r[1],r[2]+1j*r[3]])/np.sqrt(2)
        p2=np.array([r[4]+1j*r[5],r[6]+1j*r[7]])/np.sqrt(2)
        h=(r[8]+1j*r[9])/np.sqrt(2)
        x,y,s,zre,zim=invariants(r)
        self.assertAlmostEqual(x,np.vdot(p1,p1).real)
        self.assertAlmostEqual(y,np.vdot(p2,p2).real)
        self.assertAlmostEqual(s,(h.conjugate()*h).real)
        self.assertAlmostEqual(zre,np.vdot(p1,p2).real)
        self.assertAlmostEqual(zim,np.vdot(p1,p2).imag)

    def test_potential_matches_direct_complex_expression(self):
        r=np.arange(1,11,dtype=float)/11
        p1=np.array([r[0]+1j*r[1],r[2]+1j*r[3]])/np.sqrt(2)
        p2=np.array([r[4]+1j*r[5],r[6]+1j*r[7]])/np.sqrt(2)
        x=np.vdot(p1,p1).real;y=np.vdot(p2,p2).real
        z=np.vdot(p1,p2);s=(r[8]**2+r[9]**2)/2
        w=synthetic_quartics(20261020)
        direct=(w['l1']*x*x/2+w['l2']*y*y/2+w['l3']*x*y+
                w['l4']*abs(z)**2 +
                (w['l5']*z*z+2*w['l6']*x*z+2*w['l7']*y*z).real+
                w['lh']*s*s+s*(w['l8']*x+w['l9']*y+
                               2*(w['l10']*z).real))
        self.assertAlmostEqual(potential(r,tensor_for_quartics(w)),direct,places=13)

    def test_hessian_matches_finite_difference(self):
        r=np.arange(1,11,dtype=float)/12
        C=tensor_for_quartics(synthetic_quartics(20261021))
        exact=hessian(r,C)
        h=1e-4
        for i,j in ((0,0),(0,4),(2,9),(8,9)):
            di=np.eye(10)[i]*h;dj=np.eye(10)[j]*h
            fd=(potential(r+di+dj,C)-potential(r+di-dj,C)-
                potential(r-di+dj,C)+potential(r-di-dj,C))/(4*h*h)
            self.assertAlmostEqual(exact[i,j],fd,places=6)

    def test_O4_single_doublet_lambda_beta(self):
        lam=.41
        out,diag=independent_scalar_beta({'l1':lam},self.fields,self.design)
        self.assertAlmostEqual(out['l1'],12*lam*lam,places=11)
        self.assertLess(diag['projection_residual'],1e-12)
        for k in PHYSICAL_QUARTICS:
            if k!='l1':self.assertAlmostEqual(abs(out[k]),0.,places=10)

    def test_O2_complex_singlet_lambda_beta(self):
        lam=.31
        out,diag=independent_scalar_beta({'lh':lam},self.fields,self.design)
        self.assertAlmostEqual(out['lh'],20*lam*lam,places=11)
        self.assertLess(diag['projection_residual'],1e-12)
        for k in PHYSICAL_QUARTICS:
            if k!='lh':self.assertAlmostEqual(abs(out[k]),0.,places=10)

    def test_real_component_roundtrip(self):
        vals=synthetic_quartics(20261022)
        vec=couplings_to_components(vals)
        back=components_to_couplings(vec)
        for k in PHYSICAL_QUARTICS:
            self.assertAlmostEqual(abs(vals[k]-back[k]),0,places=14)

    def test_full_complex_projection_is_polynomial(self):
        couplings=synthetic_quartics(20261020)
        projected,metrics=independent_scalar_beta(couplings,self.fields,self.design)
        self.assertLess(metrics['projection_residual'],1e-12)
        self.assertLess(metrics['condition_number'],100)
        self.assertGreater(abs(projected['l10']),.01)
        self.assertGreater(abs(projected['l6']),.01)

    def test_projection_singular_basis_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'singular'):
            quartic_projection(np.zeros((16,10),float))

    def test_scalar_quartic_no_dimensional_parameters(self):
        a,ma=independent_scalar_beta({'l1':.3,'lh':.2,'l10':.04-.02j},
                                      self.fields,self.design)
        self.assertLess(ma['projection_residual'],1e-12)
        self.assertTrue(all(np.isfinite(abs(v)) for v in a.values()))

    def test_mock_export_exact_beta_comparison(self):
        expected,_=independent_scalar_beta({'l1':.31,'lh':.19},self.fields,self.design)
        functions={}
        for k,val in expected.items():
            namespace={}
            exec('def beta_'+k+'(nLoop):\n    return '+repr(val)+'\n',{},namespace)
            functions['beta_'+k]=namespace['beta_'+k]
        mock=SimpleNamespace(**functions)
        result=compare_pyrate_scalar_betas(mock,{'l1':.31,'lh':.19},expected)
        self.assertTrue(all(x['pass'] for x in result.values()),result)

    def test_wrong_portal_beta_is_detected(self):
        expected,_=independent_scalar_beta({'l8':.11,'l9':.15,'l10':.035+.027j},
                                             self.fields,self.design)
        functions={}
        for k,val in expected.items():
            namespace={}
            exec('def beta_'+k+'(nLoop):\n    return '+repr(val)+'\n',{},namespace)
            functions['beta_'+k]=namespace['beta_'+k]
        functions['beta_l10']=lambda nLoop:expected['l10']*2
        result=compare_pyrate_scalar_betas(
            SimpleNamespace(**functions),
            {'l8':.11,'l9':.15,'l10':.035+.027j},expected)
        self.assertFalse(result['l10']['pass'])

if __name__=='__main__':
    unittest.main()
