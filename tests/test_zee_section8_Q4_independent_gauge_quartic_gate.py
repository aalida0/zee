"""Independent electroweak gauge-quartic Zee RGE tests.

The gauge-boson mass matrix, SU(2)xU(1) Casimir term, 15-dimensional
projection, and fail-closed exported comparison are tested independently of
any real PyR@TE output. No UV or phenomenological acceptance claim.
"""
import pathlib
import sys
import unittest
from types import SimpleNamespace
import numpy as np

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_independent_gauge_quartic_gate import (
    SIGMA,gauge_mass_squared,quartic_gauge_linear_coefficient,
    gauge_loop_polynomial,gauge_quartic_beta,
    compare_generator,source_gauge_delta
)

class TestGaugeQuarticIndependent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rng=np.random.default_rng(20261020)
        cls.fields=cls.rng.normal(size=(128,10))

    def test_gauge_matrix_real_symmetric_and_positive(self):
        phi=self.rng.normal(size=10)
        m=gauge_mass_squared(phi,.36,.65)
        self.assertEqual(m.shape,(4,4))
        self.assertTrue(np.all(np.isfinite(m)))
        np.testing.assert_allclose(m,m.T,atol=0)
        self.assertGreaterEqual(np.min(np.linalg.eigvalsh(m)),-1e-13)

    def test_only_one_doublet_has_two_w_and_one_z_mass(self):
        phi=np.zeros(10);phi[2]=246
        m=gauge_mass_squared(phi,.36,.65)
        expected=246**2/4*np.array([.65**2,.65**2,.65**2+.36**2,0.])
        got=np.linalg.eigvalsh(m)
        np.testing.assert_allclose(np.sort(got),np.sort(expected),rtol=1e-13,atol=1e-10)

    def test_only_singlet_gives_hypercharge_mass(self):
        r=np.zeros(10);r[8]=1.8;r[9]=-.35
        gp=.41
        m=gauge_mass_squared(r,gp,0)
        expect=2*gp**2*(r[8]**2+r[9]**2)/2
        np.testing.assert_allclose(m,np.diag([0.,0.,0.,expect]),rtol=1e-13,atol=1e-14)

    def test_no_gauge_couplings_gives_zero_mass_matrix(self):
        np.testing.assert_allclose(gauge_mass_squared(self.fields[0],0,0),np.zeros((4,4)))

    def test_SM_lambda1_pure_gauge_analytic(self):
        gp,g2=.36,.65
        coeff,_=gauge_quartic_beta({},gp,g2,self.fields)
        expected=.75*(3*g2**4+2*g2**2*gp**2+gp**4)
        self.assertAlmostEqual(coeff['l1'],expected,places=12)
        self.assertAlmostEqual(coeff['l2'],expected,places=12)

    def test_scalar_QED_lh_and_portal_analytic(self):
        gp=.36
        coeff,_=gauge_quartic_beta({},gp,0,self.fields)
        self.assertAlmostEqual(coeff['lh'],6*gp**4,places=12)
        self.assertAlmostEqual(coeff['l8'],3*gp**4,places=12)
        self.assertAlmostEqual(coeff['l9'],3*gp**4,places=12)

    def test_2HDM_l4_pure_mixed_gauge_analytic(self):
        gp,g2=.36,.65
        coeff,_=gauge_quartic_beta({},gp,g2,self.fields)
        self.assertAlmostEqual(coeff['l4'],3*g2*g2*gp*gp,places=12)
        self.assertAlmostEqual(coeff['l3'],
          .75*(3*g2**4-2*g2*g2*gp*gp+gp**4),places=12)

    def test_no_pure_gauge_source_for_complex_quartics(self):
        coeff,_=gauge_quartic_beta({},.36,.65,self.fields)
        for name in ('l5','l6','l7','l10'):
            self.assertLess(abs(coeff[name]),1e-12)

    def test_universal_doublet_wavefunction_coefficient(self):
        gp,g2=.36,.65
        expected=-(9*g2*g2+3*gp*gp)
        for k in ('l1','l2','l3','l4','l5','l6','l7'):
            self.assertAlmostEqual(quartic_gauge_linear_coefficient(k,gp,g2),
                                   expected,places=13)

    def test_portal_and_singlet_wavefunction(self):
        gp,g2=.36,.65
        for k in ('l8','l9','l10'):
            self.assertAlmostEqual(quartic_gauge_linear_coefficient(k,gp,g2),
                                   -(4.5*g2**2+7.5*gp**2),places=13)
        self.assertAlmostEqual(quartic_gauge_linear_coefficient('lh',gp,g2),
                               -12*gp**2,places=13)

    def test_independently_projected_complex_portals(self):
        q={'l8':.12,'l9':.11,'l10':.031+.014j,'l6':.02-.018j}
        got,fit=gauge_quartic_beta(q,.36,.65,self.fields)
        self.assertLess(fit['projection_residual'],1e-12)
        self.assertLess(fit['condition_number'],1e5)
        # Gauge g^4 alone cannot seed lambda10 without its own quartic.
        self.assertAlmostEqual(got['l10'],
          -(4.5*.65**2+7.5*.36**2)*q['l10'],places=11)

    def test_zero_gauge_couplings_zero_gauge_beta(self):
        got,_=gauge_quartic_beta({'l1':.3,'l10':.03+.04j},0.,0.,self.fields)
        self.assertTrue(all(abs(x)<1e-12 for x in got.values()))

    def test_bad_gauge_inputs_fail(self):
        with self.assertRaises(ValueError):
            gauge_quartic_beta({},-.1,.65,self.fields)
        with self.assertRaises(ValueError):
            gauge_quartic_beta({},np.nan,.65,self.fields)

    def test_mock_export_gauge_difference_matches(self):
        """Check the comparator on independent gauge-sector expectations."""
        q={'l1':.33,'l10':.03+.02j}
        gp,g2=.36,.65
        # Functions here are synthetic fixtures, not physical cross-checks.
        def make_beta(name):
            def fn(nLoop,gp,g2,l1,l10):
                qq={'l1':l1,'l10':l10}
                # Fixture deliberately computes gauge difference at call time.
                return gauge_quartic_beta(qq,gp,g2,self.fields)[0][name]
            return fn
        mock=SimpleNamespace(**{'beta_'+k:make_beta(k)
                   for k in ('l1','l2','l3','l4','l5','l6','l7',
                             'lh','l8','l9','l10')})
        independent,_=gauge_quartic_beta(q,gp,g2,self.fields)
        rows=compare_generator(mock,q,gp,g2,independent)
        self.assertEqual(len(rows),11)
        self.assertTrue(all(x['pass'] for x in rows.values()),rows)
        mock.beta_l8=lambda nLoop,gp,g2,l1,l10: 2*independent['l8']
        rows=compare_generator(mock,q,gp,g2,independent)
        self.assertFalse(rows['l8']['pass'])

if __name__=="__main__":
    unittest.main()
