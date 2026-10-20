"""Q4v13 integrated full-Zee one-loop diagnostic regression tests.

These checks are unit-scale sanity tests for the SINGLE large 676-comparison
AF end-to-end gate. Synthetic inputs are NOT neutrino- or LFV-allowed.
"""
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_large_integrated_one_loop_gate import (
    NAMES,REAL_NAMES,MATRIX_NAMES,
    baseline,typeii_boundary,validate_state,
    combined_dimensional_beta,
    independent_full_beta,compare_state,full_source_beta,
    rk4_step,add_state,
)
from zee_section8_Q4_independent_scalar_hessian_gate import (
    quartic_projection,PHYSICAL_QUARTICS,
)
from zee_section8_Q4_independent_dimensional_scalar_gate import projected_bases

def gauge_only():
    z=baseline(20261101)
    for k in PHYSICAL_QUARTICS:z[k]=0.
    for k in MATRIX_NAMES:z[k]=np.matrix(np.zeros((3,3),complex))
    z.update({'muZee':0.,'m12':0.})
    return z

class TestQ4LargeOneLoop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=np.random.default_rng(20261019)
        cls.fields=rng.normal(size=(72,10))
        cls.quartic_basis=quartic_projection(cls.fields)
        cls.dimension_basis=projected_bases(cls.fields)

    def test_full_26_inventory(self):
        self.assertEqual(len(NAMES),26)
        self.assertEqual(len(MATRIX_NAMES),7)
        self.assertEqual(set(NAMES),
                         set(baseline(20261101)))
        self.assertEqual(set(MATRIX_NAMES),
                         {'Yu1','Yu2','Yd1','Yd2','Ye1','Ye2','f'})

    def test_three_complex_independent_reference_points_finite(self):
        for seed in range(20261101,20261104):
            s=baseline(seed)
            out,_=independent_full_beta(
                s,self.fields,self.quartic_basis,self.dimension_basis)
            self.assertEqual(set(out),set(NAMES))
            self.assertTrue(all(np.isfinite(np.asarray(v)).all()
                                for v in out.values()))
            self.assertLess(np.max(abs(out['f']+out['f'].T)),1e-12)

    def test_complex_rephased_point_has_same_nonzero_inventory(self):
        from zee_section8_Q4_complex_lepton_scalar_covariance_gate import field_rephase
        s=baseline(20261102)
        rotated=field_rephase(s,.67,-.32)
        validate_state(rotated)
        self.assertGreater(abs(rotated['l10']),.001)
        self.assertGreater(np.linalg.norm(rotated['Ye2']),.001)

    def test_gauge_only_mass_wave_coefficients(self):
        s=gauge_only()
        s.update({'m1':81000.,'m2':65000.,
                  'mchi':129000.,'m12':21000.+7000j})
        bet,diag=combined_dimensional_beta(
            s,self.fields,self.dimension_basis)
        gp=float(s['gp']);g2=float(s['g2'])
        gd=-4.5*g2*g2-1.5*gp*gp
        self.assertAlmostEqual(bet['m1'],gd*s['m1'],delta=1e-7)
        self.assertAlmostEqual(bet['m2'],gd*s['m2'],delta=1e-7)
        self.assertAlmostEqual(bet['mchi'],-6*gp*gp*s['mchi'],delta=1e-7)
        self.assertLess(abs(bet['m12']-gd*s['m12']),1e-7)
        self.assertLess(abs(bet['muZee']),1e-10)
        self.assertLess(
            diag['gauge_and_Yukawa_mass_projection_residual'],1e-10)

    def test_pure_f_charged_singlet_mass_and_mu(self):
        s=gauge_only()
        s['gp']=0.;s['g2']=0.
        from zee_section8_Q4_independent_f_quartic_gate import synthetic_f
        s['f']=np.matrix(synthetic_f(20261019))
        s.update({'m1':0.,'m2':0.,'mchi':129000.,
                  'm12':0.,'muZee':0.})
        pure_mass,_=combined_dimensional_beta(
            s,self.fields,self.dimension_basis)
        trace=float(np.trace(s['f'].H@s['f']).real)
        self.assertAlmostEqual(pure_mass['mchi'],8*trace*s['mchi'],delta=1e-7)
        s['muZee']=220.+55j
        with_mu,_=combined_dimensional_beta(
            s,self.fields,self.dimension_basis)
        self.assertAlmostEqual(with_mu['muZee'].real,
            4*trace*s['muZee'].real,delta=1e-8)
        # Cubic scalar loop also produces additive masses from |mu|^2.
        self.assertGreater(with_mu['m1'],pure_mass['m1'])
        self.assertGreater(with_mu['m2'],pure_mass['m2'])
        self.assertGreater(with_mu['mchi'],pure_mass['mchi'])

    def test_top_only_higgs_mass_and_zee_cubic_wave(self):
        s=gauge_only()
        s['gp']=0.;s['g2']=0.
        yt=.93
        s['Yu2']=np.matrix(np.diag((0.,0.,yt)))
        s.update({'m1':0.,'m2':151000.,
                  'mchi':0.,'m12':0.,'muZee':230.})
        bet,_=combined_dimensional_beta(
            s,self.fields,self.dimension_basis)
        # beta_m2 Yukawa coefficient is 6 yt^2; mu beta is 3 yt^2.
        self.assertAlmostEqual(bet['muZee'].real,
                               3*yt**2*230,delta=1e-9)
        self.assertGreater(bet['m2'],6*yt**2*151000-1e-7)
        self.assertLess(abs(bet['m12']),1e-7)

    def test_generic_dimensionful_projection_closes(self):
        for seed in (20261101,20261102,20261103):
            s=baseline(seed)
            _,metrics=combined_dimensional_beta(
                s,self.fields,self.dimension_basis)
            self.assertLess(
                metrics['gauge_and_Yukawa_mass_projection_residual'],1e-11)

    def test_fzero_typeii_wrong_doublet_tangent(self):
        s=typeii_boundary()
        self.assertEqual(np.linalg.norm(s['Yd2']),0.)
        self.assertEqual(np.linalg.norm(s['Yu1']),0.)
        beta,_=independent_full_beta(s,self.fields,self.quartic_basis,self.dimension_basis)
        self.assertGreater(np.linalg.norm(beta['Yd2']),1e-8)
        self.assertGreater(np.linalg.norm(beta['Yu1']),1e-8)

    def test_comparator_mutated_mass_and_complex_portal_detected(self):
        s=baseline(20261101)
        ref,_=independent_full_beta(
            s,self.fields,self.quartic_basis,self.dimension_basis)
        exact,bad=compare_state(ref,ref)
        self.assertFalse(bad)
        self.assertEqual(len(exact),26)
        altered=dict(ref)
        altered['mchi']=ref['mchi']+.2
        altered['l10']=ref['l10']+(.02+.01j)
        altered['Ye2']=ref['Ye2']+.02*np.eye(3)
        _,bad=compare_state(altered,ref)
        self.assertEqual(set(bad),{'mchi','l10','Ye2'})

    def test_rk4_zero_beta_preserves_all_26_couplings(self):
        s=baseline(20261101)
        funcs={}
        for k in NAMES:
            shape=(3,3) if k in MATRIX_NAMES else ()
            value=np.zeros(shape,complex) if shape else 0.
            funcs['beta_'+k]=(lambda ret=value: lambda nLoop:ret)()
        fake=SimpleNamespace(**funcs)
        flowed=rk4_step(fake,s,.20)
        for name in NAMES:
            np.testing.assert_allclose(np.asarray(flowed[name]),
                                       np.asarray(s[name]),atol=1e-14)

    def test_add_state_rejects_real_part_imaginary_perturbation(self):
        s=baseline(20261101)
        beta={k:(np.zeros((3,3),complex)
                   if k in MATRIX_NAMES else 0.) for k in NAMES}
        beta['m1']=.7j
        with self.assertRaisesRegex(ValueError,'real manifold'):
            add_state(s,beta,.1)

if __name__=='__main__':
    unittest.main()
