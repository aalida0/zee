"""Source-normalized independent nonzero-f Zee scalar-quartic one-loop tests.

Independent 9x9 symmetric Weyl lepton mass matrix + charged singlet
anomalous dimension. All tests use synthetic examples, never allowed points.
"""
from pathlib import Path
import sys
import unittest
import numpy as np
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_independent_f_quartic_gate import (
    validate_f,synthetic_f,lepton_weyl_mass,fermion_box_delta,
    singlet_wave_delta,f_quartic_polynomial,independent_f_quartic_betas,
    compare_source,
)
from zee_section8_Q4_independent_scalar_hessian_gate import (
    PHYSICAL_QUARTICS,synthetic_quartics,
)
from zee_section8_Q4_independent_yukawa_quartic_gate import (
    YUKAWAS,synthetic_yukawas,
)
from zee_section8_Q4_complex_lepton_scalar_covariance_gate import (
    field_rephase,
)
from zee_section8_Q4_independent_gauge_quartic_gate import (
    complex_doublets_and_singlet,
)

def zeros():
    return {k:np.zeros((3,3),complex) for k in YUKAWAS}

class TestQ4FDependentQuartic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=np.random.default_rng(20261019)
        cls.fields=rng.normal(size=(96,10))
        cls.f=synthetic_f(20261019)
        cls.yy=synthetic_yukawas(20261020)

    def test_complex_f_is_exactly_antisymmetric(self):
        f=validate_f(self.f)
        self.assertEqual(f.shape,(3,3))
        self.assertLess(np.max(abs(f+f.T)),1e-14)
        self.assertGreater(np.max(abs(f.imag)),1e-4)

    def test_wrong_f_symmetry_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'antisymmetric'):
            validate_f(np.ones((3,3),complex))

    def test_wrong_f_shape_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'3x3'):
            validate_f(np.ones((2,2),complex))

    def test_weyl_mass_is_symmetric_and_nine_by_nine(self):
        m=lepton_weyl_mass(self.fields[3],self.yy,self.f)
        self.assertEqual(m.shape,(9,9))
        self.assertLess(np.max(abs(m-m.T)),1e-14)
        self.assertTrue(np.isfinite(m).all())

    def test_mass_f_block_is_two_f_chi(self):
        r=np.zeros(10)
        r[8]=.71;r[9]=-.22
        m=lepton_weyl_mass(r,zeros(),self.f)
        chi=(r[8]+1j*r[9])/np.sqrt(2)
        np.testing.assert_allclose(m[:3,3:6],2*self.f*chi)
        np.testing.assert_allclose(m[3:6,:3],(2*self.f*chi).T)
        self.assertLess(np.max(abs(m[:6,6:])),1e-14)

    def test_f_zero_exactly_decouples(self):
        zero=np.zeros((3,3),complex)
        for r in (self.fields[1],self.fields[8]):
            self.assertAlmostEqual(fermion_box_delta(r,self.yy,zero),0.,places=12)
            self.assertAlmostEqual(singlet_wave_delta(r,{'lh':.34},zero),0.,places=12)

    def test_Kanemura_real_f_singlet_box_limit(self):
        f=np.array([[0,.12,-.05],[-.12,0,.09],[.05,-.09,0]],float)
        got,_=independent_f_quartic_betas({},zeros(),f,self.fields)
        expected=-32*np.trace((f.T@f)@(f.T@f))
        self.assertAlmostEqual(got['lh'],expected,places=11)
        for k in PHYSICAL_QUARTICS:
            if k!='lh':
                self.assertLess(abs(got[k]),1e-11)

    def test_Kanemura_real_f_wavefunction_limit(self):
        f=np.array([[0,.12,-.05],[-.12,0,.09],[.05,-.09,0]],float)
        l=.3
        full,_=independent_f_quartic_betas({'lh':l},zeros(),f,self.fields)
        box,_=independent_f_quartic_betas({},zeros(),f,self.fields)
        trace=float(np.trace(f.T@f))
        self.assertAlmostEqual(full['lh']-box['lh'],16*trace*l,places=10)

    def test_general_complex_f_singlet_formula(self):
        q={'lh':.23}
        full,diag=independent_f_quartic_betas(q,zeros(),self.f,self.fields)
        d=self.f.conj().T@self.f
        expect=16*np.trace(d).real*q['lh']-32*np.trace(d@d).real
        self.assertAlmostEqual(full['lh'],expect,places=10)
        self.assertLess(diag['projection_residual'],1e-12)

    def test_portals_f_wavefunction_without_lepton_yukawas(self):
        q={'l8':.14,'l9':.16,'l10':.037+.018j}
        d=float(np.trace(self.f.conj().T@self.f).real)
        full,_=independent_f_quartic_betas(q,zeros(),self.f,self.fields)
        for k in ('l8','l9','l10'):
            self.assertLess(abs(full[k]-8*d*q[k]),1e-10)
        for k in ('l1','l2','l3','l4','l5','l6','l7'):
            self.assertLess(abs(full[k]),1e-11)

    def test_mixed_nonzero_f_ye_closes_all_15_real_components(self):
        q=synthetic_quartics(20261021)
        c,diag=independent_f_quartic_betas(q,self.yy,self.f,self.fields)
        self.assertEqual(set(c),set(PHYSICAL_QUARTICS))
        self.assertLess(diag['projection_residual'],1e-11)
        self.assertLess(diag['projection_condition_number'],1e5)

    def test_f_never_changes_pure_doublet_quartic_betas(self):
        c,_=independent_f_quartic_betas(
            synthetic_quartics(20261020),self.yy,self.f,self.fields)
        for k in ('l1','l2','l3','l4','l5','l6','l7'):
            self.assertLess(abs(c[k]),1e-10)

    def test_f_box_phase_invariance(self):
        v=fermion_box_delta(self.fields[3],self.yy,self.f)
        w=fermion_box_delta(self.fields[3],self.yy,
                            np.exp(.37j)*self.f)
        self.assertAlmostEqual(v,w,places=12)

    def test_f_wavefunction_quadratic_scaling(self):
        r=self.fields[4]
        q={'lh':.32,'l8':.09,'l10':.024+.01j}
        one=singlet_wave_delta(r,q,self.f)
        two=singlet_wave_delta(r,q,2*self.f)
        self.assertAlmostEqual(two,4*one,places=11)

    def test_box_quartic_f_scaling_without_other_yukawas(self):
        r=self.fields[7]
        one=fermion_box_delta(r,zeros(),self.f)
        double=fermion_box_delta(r,zeros(),2*self.f)
        self.assertAlmostEqual(double,16*one,places=10)

    def test_complex_rephasing_of_f_ye_and_scalars(self):
        r=np.array(self.fields[7],copy=True)
        theta,psi=.39,-.54
        h1,h2,chi=complex_doublets_and_singlet(r)
        r2=r.copy()
        hr=np.exp(1j*theta)*h2
        sr=np.exp(1j*psi)*chi
        r2[4:8]=np.array((np.sqrt(2)*hr[0].real,
                         np.sqrt(2)*hr[0].imag,
                         np.sqrt(2)*hr[1].real,
                         np.sqrt(2)*hr[1].imag))
        r2[8:]=np.array((np.sqrt(2)*sr.real,np.sqrt(2)*sr.imag))
        quartics=synthetic_quartics(20261020)
        allvalues={**self.yy,**quartics,'f':self.f}
        changed=field_rephase(allvalues,theta,psi)
        original=f_quartic_polynomial(r,quartics,self.yy,self.f)
        transformed=f_quartic_polynomial(
            r2,{k:changed[k] for k in quartics},
            {k:changed[k] for k in self.yy},changed['f'])
        self.assertAlmostEqual(original,transformed,places=10)

    def test_mock_generated_beta_difference_comparison(self):
        q={'lh':.27,'l8':.14,'l10':.022+.013j}
        expected,_=independent_f_quartic_betas(q,self.yy,self.f,self.fields)
        # Fake beta is a fixture which is zero for f=0 and matches
        # independent value for this exact nonzero f; not a physics check.
        def make_fn(value):
            def beta(nLoop,f):
                return value if np.max(abs(f))>0 else 0.
            return beta
        funcs={'beta_'+k:make_fn(v) for k,v in expected.items()}
        mock=SimpleNamespace(**funcs)
        tested=compare_source(mock,q,self.yy,self.f,expected)
        self.assertTrue(all(v['pass'] for v in tested.values()),tested)
        mock.beta_lh=make_fn(2*expected['lh'])
        tested=compare_source(mock,q,self.yy,self.f,expected)
        self.assertFalse(tested['lh']['pass'])

if __name__=="__main__":
    unittest.main()
