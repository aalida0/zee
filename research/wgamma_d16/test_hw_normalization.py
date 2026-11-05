"""Bounded D16 HW audit. One expected failure explicitly retains upstream bug."""
import copy
import unittest
import numpy as np

from .external_2hdm_hw_override import (GROUPS, REFERENCE, ROOT, ML, STATUS,
    candidates, load_reference, run)


def vector(x):
    a = np.asarray(x)
    return a[..., 0]+1j*a[..., 1]


class HWNormalization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = run()
        cls.ref = load_reference(REFERENCE)

    def test_generic_complex_coherent_closure_and_falsifiers(self):
        records = self.evidence['records']
        self.assertEqual(self.evidence['status'], STATUS)
        self.assertEqual(len(records), 13)
        for r in records:
            for c in r['channels']:
                total = vector(c['PAPER_CORRECTED_HW'])
                hw = vector(c['corrected_HW'])
                np.testing.assert_allclose(vector(c['corrected_two_loop']),
                                           vector(c['mapped_two_loop']), rtol=3e-11, atol=3e-18)
                np.testing.assert_allclose(total-vector(c['AUTHOR_UNMODIFIED']),
                                           vector(c['difference']), rtol=3e-11, atol=3e-17)
                if not r['name'].startswith('control'):
                    self.assertTrue(np.all(abs(total.imag) > 1e-10))
                    self.assertTrue(np.all(abs(hw) > 1e-12))
                    self.assertTrue(all(v > 1e-14 for v in c['leave_one_out_abs_residual'].values()))
                    self.assertGreater(c['HW_zero_falsifier_abs'], 1e-10)
                    self.assertLess(max(c['group_relative_residual'].values()), 3e-11)
                else:
                    self.assertLess(max(abs(hw)), 1e-13)

    def test_native_hessian_and_independent_signed_operator_conversion(self):
        from module3.tree import G, PL, PR
        from module4.matching_audit import sigma
        for r in self.evidence['records']:
            self.assertLess(max(r['scalar']['G_hessian_abs_residual_GeV'].values()), 3e-10)
        # Derive the equality as signed action vertices, including the photon
        # derivative and i from the action; no positive-rate sign inference.
        q = np.array([1., 0., 0., 1.]); eps = np.array([0., 1., 0., 0.])
        metric = np.diag([1., -1., -1., -1.])
        qc, ec = metric@q, metric@eps
        field = 1j*(np.outer(qc, ec)-np.outer(ec, qc))
        c = np.array([.03+.02j, -.07+.01j]); v, mi, e = 246., .106, .313
        converted = -c/(8*np.pi**2*v*v)
        external = []
        for pref, lr in [(-e*mi/(16*np.pi**2*v*v), c), (e*mi/2, converted)]:
            X = lr[0]*PL+lr[1]*PR
            external.append(1j*pref*sum(sigma(m,n)@X*field[m,n] for m in range(4) for n in range(4)))
        self.assertGreater(np.linalg.norm(external[0]), 1e-10)
        np.testing.assert_allclose(external[0], external[1], rtol=2e-15, atol=1e-24)
        # The CP-odd part of ONE Hermitian chiral pair is -i a Im(cR) sigma g5.
        cr = .07+.03j; a = e*mi/(16*np.pi**2*v*v)
        chiral = -a*(cr.conjugate()*PL+cr*PR)
        edm = 2*a*cr.imag
        np.testing.assert_allclose(chiral-chiral.trace()/4*np.eye(4),
                                   -1j*edm/2*(PR-PL), rtol=1e-14, atol=1e-24)
        np.testing.assert_allclose(G[0]@(sigma(0,1)@PR).conj().T@G[0], sigma(0,1)@PL)

    def test_captured_edm_identity_and_integral_masters(self):
        checks = self.evidence['edm_checks']
        self.assertEqual(len(checks), 39)
        for c in checks:
            np.testing.assert_allclose(c['operator_prediction_GeV_minus1'],
                c['captured_EDM_GeV_minus1'], rtol=4e-11, atol=1e-25)
        for c in self.evidence['master_checks']:
            np.testing.assert_allclose(c['author'], c['integral'], rtol=5e-9, atol=2e-8)
        hw = next(c for c in checks if c['name']=='G1' and c['group']=='HW')
        self.assertGreater(abs(hw['captured_EDM_GeV_minus1']), 1e-16)
        self.assertGreater(abs(hw['operator_prediction_GeV_minus1']/hw['original_source_prediction_GeV_minus1']), 1000)

    @unittest.expectedFailure
    def test_original_author_HW_diagonal_operator_normalization_EXPECTED_FAIL(self):
        # Explicit upstream failure. Never mark a patched upstream checkout PASS.
        c = next(c for c in self.evidence['edm_checks'] if c['name']=='G1' and c['group']=='HW')
        np.testing.assert_allclose(c['original_source_prediction_GeV_minus1'],
            c['captured_EDM_GeV_minus1'], rtol=1e-10, atol=0)

    def test_homogeneity_and_potential_sign_mass_weak_angle_phase_variations(self):
        for h in self.evidence['homogeneity']:
            self.assertLess(max(h['abs_residuals'].values()), 3e-13)
        rows = {r['name']:r for r in self.evidence['records']}
        for key in ('G1', 'G2', 'G3'):
            self.assertEqual(rows[key]['scalar']['bfb']['assessment'], 'PASS')
            self.assertEqual(rows[key]['scalar']['unitarity_assessment'], 'PASS')
        for key in ('Z3_sign', 'Z7_sign', 'both_signs', 'mass', 'angle', 'MW76', 'MW84'):
            self.assertGreater(max(abs(vector(rows[key]['channels'][0]['corrected_HW'])
                                      -vector(rows['G1']['channels'][0]['corrected_HW']))), 1e-9)
        phases = np.array([.37, -.81, .22])
        for original, rotated in zip(rows['G1']['channels'], rows['phase']['channels']):
            i, j = original['channel']
            for key in ('AUTHOR_UNMODIFIED', 'PAPER_CORRECTED_HW', 'corrected_HW'):
                np.testing.assert_allclose(vector(rotated[key]), vector(original[key])
                    *np.exp(1j*(phases[i-1]-phases[j-1])), rtol=3e-12, atol=1e-17)

    def test_source_preserving_replacement_and_closed_zee_gate(self):
        row = self.evidence['records'][0]['channels'][0]
        groups = {g:vector(v) for g,v in row['author_groups'].items()}
        before = copy.deepcopy(groups)
        replacement = vector(row['corrected_HW'])
        result = candidates(groups, replacement)
        for g in GROUPS:
            np.testing.assert_array_equal(groups[g], before[g])
            if g != 'HW':
                np.testing.assert_array_equal(result['corrected_groups'][g], before[g])
        with self.assertRaises(ValueError):
            candidates({'HW':groups['HW']}, replacement)
        load_reference(REFERENCE)  # verifies pinned original bytes after execution
        from .matching import example, evaluate
        r = evaluate(example())
        self.assertIsNone(r['C_L']); self.assertIsNone(r['C_R'])
        self.assertFalse(r['coherent_inclusion'])


class RestrictedZeeClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from .external_2hdm_hw_override import fixtures, example_input
        cls.ref = load_reference(REFERENCE)
        _, p, cls.D, _ = fixtures(cls.ref, example_input(REFERENCE))[0]
        cls.p = dict(p, mH2=540., k1=.3, k2=.18, k12=-.04)

    def test_singlet_HZ_integral_charge_and_Ward_completed_partners(self):
        from .zee_singlet_hz import hz_radial_kernel
        from module4.charged_scalar import scalar_qed_tensor, scalar_loop_kernel
        for x,y in ((.3,.5),(1.,.1),(3.,.2),(1.7,1.)):
            value, error = hz_radial_kernel(x,y)
            self.assertLess(error, 1e-8)
            if y != 1:
                np.testing.assert_allclose(value, self.ref.f10(x,y), rtol=1e-11)
                divided = -2*(scalar_loop_kernel(x/y)[0]-scalar_loop_kernel(x)[0])/(1-y)
                np.testing.assert_allclose(value, divided, rtol=1e-11)
            else:
                near = hz_radial_kernel(x, 1.00001)[0]
                self.assertLess(abs(value-near), 1e-6)
        # Replacing the second current by a diagonal Z charge multiplies the
        # complete Abelian tensor, including AZ contact, by tZ/Q.
        p = np.array([.2,.3,-.4,.1]); q = np.array([1.,.3,.2,-.2])
        triangle, contact = scalar_qed_tensor(p,q)
        tz = -np.sqrt(1-80.379**2/91.1876**2)/(80.379/91.1876)
        tensor = tz*(triangle+contact)
        self.assertLess(max(abs(p@tensor)), 2e-13)
        self.assertLess(max(abs(tensor@q)), 2e-13)
        self.assertGreater(max(abs(p@(tz*triangle))), .01)

    def test_singlet_HZ_three_complex_channels_limits_and_restrictions(self):
        from .zee_singlet_hz import singlet_hz
        f = np.zeros((3,3),complex)
        for i,j in ((1,0),(2,0),(2,1)):
            args = (self.D,f,self.p,ML,80.379,91.1876,i,j)
            r = singlet_hz(*args)
            value = r['class_C_LR_GeV_minus2']
            self.assertTrue(np.all(abs(value.imag)>1e-18))
            self.assertFalse(r['coherent_inclusion'])
            zero = singlet_hz(self.D,f,dict(self.p,k1=0.,k2=0.,k12=0.),ML,80.379,91.1876,i,j)
            np.testing.assert_array_equal(zero['class_C_LR_GeV_minus2'], np.zeros(2))
            heavy = singlet_hz(self.D,f,dict(self.p,mH2=5400.),ML,80.379,91.1876,i,j)
            self.assertLess(max(abs(heavy['class_C_LR_GeV_minus2'])), max(abs(value))/20)
        for p,ff in [(dict(self.p,gamma=.1),f), (self.p,np.eye(3)*.01)]:
            with self.assertRaises(ValueError):
                singlet_hz(self.D,ff,p,ML,80.379,91.1876,1,0)


if __name__ == '__main__':
    unittest.main()
