"""Q4v9 independent f=0 fermionic quartic one-loop regression tests.

The reference is fermion mass traces plus an independently constructed
Higgs-field wavefunction term; not the PyR@TE scalar beta formulas.
"""
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_independent_yukawa_quartic_gate import (
    YUKAWAS,validate_yukawas,dirac_masses,yukawa_higgs_trace,
    fermionic_quartic_polynomial,yukawa_quartic_beta,
    synthetic_yukawas,delta_bilinears,compare_source,
    source_yukawa_delta,
)
from zee_section8_Q4_independent_scalar_hessian_gate import (
    PHYSICAL_QUARTICS,synthetic_quartics,
)

def empty_yy():
    return {name:np.zeros((3,3),complex) for name in YUKAWAS}

class TestIndependentYukawaQuartic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rng=np.random.default_rng(20261019)
        cls.fields=cls.rng.normal(size=(96,10))

    def test_six_matrix_inventory_and_shapes(self):
        y=synthetic_yukawas(20261019)
        self.assertEqual(set(y),set(YUKAWAS))
        self.assertTrue(all(v.shape==(3,3) for v in y.values()))
        self.assertEqual(len(validate_yukawas(y)),6)

    def test_invalid_yukawa_shapes_fail_closed(self):
        y=empty_yy();y['Ye2']=np.zeros((3,2))
        with self.assertRaisesRegex(ValueError,'Invalid'):
            validate_yukawas(y)

    def test_invalid_yukawa_missing_matrix_fail_closed(self):
        y=empty_yy();del y['Yu1']
        with self.assertRaisesRegex(ValueError,'six'):
            validate_yukawas(y)

    def test_dirac_mass_shape_and_neutral_top_mass(self):
        y=empty_yy()
        y['Yu2']=np.diag((0.,0.,.93))
        r=np.zeros(10);r[6]=246.
        Mq,Me=dirac_masses(r,y)
        self.assertEqual(Mq.shape,(6,6))
        self.assertEqual(Me.shape,(6,3))
        self.assertAlmostEqual(abs(Mq[2,2]),246*.93/np.sqrt(2))
        self.assertLess(np.max(abs(Me)),1e-14)
        self.assertAlmostEqual(np.linalg.norm(Mq)**2,(246*.93/np.sqrt(2))**2)

    def test_weyl_doublet_higgs_anomalous_matrix_hermitian(self):
        yy=synthetic_yukawas(20261020)
        t=yukawa_higgs_trace(yy)
        self.assertEqual(t.shape,(2,2))
        np.testing.assert_allclose(t,t.conj().T,atol=1e-12)
        self.assertTrue(np.all(np.linalg.eigvalsh(t)>=-1e-12))

    def test_zero_yukawa_gives_zero_quartic_beta(self):
        out,fit=yukawa_quartic_beta(
            synthetic_quartics(20261020),empty_yy(),self.fields)
        self.assertLess(fit['projection_residual'],1e-12)
        self.assertLess(max(abs(v) for v in out.values()),1e-11)

    def test_top_yukawa_only_beta_l2_minus12_y4(self):
        y=.93
        yy=empty_yy()
        yy['Yu2']=np.diag((0,0,y))
        out,fit=yukawa_quartic_beta({},yy,self.fields)
        self.assertAlmostEqual(out['l2'],-12*y**4,places=10)
        self.assertLess(fit['projection_residual'],1e-12)
        for k in PHYSICAL_QUARTICS:
            if k!='l2':self.assertLess(abs(out[k]),1e-10)

    def test_top_with_lambda2_gives_plus12_lambda2_y2(self):
        y=.93;lam=.38
        yy=empty_yy();yy['Yu2']=np.diag((0,0,y))
        a,_=yukawa_quartic_beta({'l2':lam},yy,self.fields)
        b,_=yukawa_quartic_beta({},yy,self.fields)
        self.assertAlmostEqual(a['l2']-b['l2'],12*lam*y*y,places=10)

    def test_lepton_only_beta_l1_minus4_y4(self):
        y=.12
        yy=empty_yy()
        yy['Ye1']=np.diag((y,0.,0.))
        out,_=yukawa_quartic_beta({},yy,self.fields)
        self.assertAlmostEqual(out['l1'],-4*y**4,places=11)

    def test_lepton_only_l1_wavefunction_coefficient(self):
        y=.12;lam=.37
        yy=empty_yy();yy['Ye1']=np.diag((y,0.,0.))
        a,_=yukawa_quartic_beta({'l1':lam},yy,self.fields)
        b,_=yukawa_quartic_beta({},yy,self.fields)
        self.assertAlmostEqual(a['l1']-b['l1'],4*lam*y*y,places=10)

    def test_higgs_singlet_portal_yukawa_wavefunction(self):
        yy=empty_yy();yy['Yu1']=np.diag((0,0,.8))
        lam=.19
        a,_=yukawa_quartic_beta({'l8':lam},yy,self.fields)
        # T_11=3*y_t², so beta_l8=2*T11*l8.
        self.assertAlmostEqual(a['l8'],6*.8**2*lam,places=11)
        self.assertLess(abs(a['l9']),1e-11)

    def test_full_complex_quartic_closure(self):
        yy=synthetic_yukawas(20261019)
        q=synthetic_quartics(20261021)
        output,fit=yukawa_quartic_beta(q,yy,self.fields)
        self.assertEqual(set(output),set(PHYSICAL_QUARTICS))
        self.assertLess(fit['projection_residual'],1e-12)
        self.assertLess(fit['condition_number'],1e5)
        self.assertTrue(all(np.isfinite(abs(x)) for x in output.values()))

    def test_fermion_box_scales_as_y4(self):
        yy=synthetic_yukawas(20261021)
        phi=self.fields[7]
        zero=fermionic_quartic_polynomial(phi,{},yy)
        triple=fermionic_quartic_polynomial(
            phi,{}, {k:3*v for k,v in yy.items()})
        self.assertAlmostEqual(triple/(zero*81),1.,places=11)

    def test_wavefunction_term_scales_as_y2(self):
        yy=synthetic_yukawas(20261021)
        a=delta_bilinears(self.fields[8],yy)
        b=delta_bilinears(self.fields[8],{k:2*v for k,v in yy.items()})
        np.testing.assert_allclose(b,4*a,rtol=1e-12,atol=1e-14)

    def test_mock_output_comparison_detects_wrong_l10(self):
        q={'l1':.31,'l10':.025+.011j}
        yy=empty_yy();yy['Yu1']=np.diag((0,0,.93))
        independent,_=yukawa_quartic_beta(q,yy,self.fields)
        def make_mock_beta(value):
            def fake_beta(nLoop,Yu1):
                return value if np.max(np.abs(Yu1))>0 else 0.
            return fake_beta
        funcs={'beta_'+k:make_mock_beta(v) for k,v in independent.items()}
        mod=SimpleNamespace(**funcs)
        checks=compare_source(mod,q,yy,independent)
        self.assertEqual(len(checks),11)
        self.assertTrue(all(v['pass'] for v in checks.values()))
        mod.beta_l10=make_mock_beta(2*independent['l10'])
        checks=compare_source(mod,q,yy,independent)
        self.assertFalse(checks['l10']['pass'])

if __name__=='__main__':
    unittest.main()
