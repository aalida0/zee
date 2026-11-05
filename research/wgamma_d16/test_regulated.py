"""New integral/ST tests only. No physical gauge-matching PASS is granted."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import sympy as s

from .algebra import decay_momenta, dot, GAMMA, PL, source_tensors
from .longitudinal_identities import scalar_contraction, contracted_triple
from .matching import evaluate, example
from .native_integrands import xi1_graphs
from .parent_integrals import (calculate_parent, calculate_native_parents, numerator,
    native_parent_numerator, pointwise_pinch_residual, calculate_parent_rxi, exact_parent_integrand)
from .tensor_reduction import (calculate, calculate_longitudinal, exact_uv, reduce_general,
                               reduce_rank2)

HERE = Path(__file__).resolve().parent


class RegulatedTests(unittest.TestCase):
    def test_exact_arbitrary_xi_all_inner_uv_poles(self):
        poles = exact_uv()
        self.assertEqual(poles['total'], dict.fromkeys(('g', 'qq', 'qk', 'kq', 'kk'), 0))
        self.assertEqual(len(poles['graphs']), 26)
        # These are nonzero diagrams; absence of poles in the sum is a cancellation.
        self.assertNotEqual(poles['graphs']['triangle_WWW_+1']['g'], 0)

    def test_independent_rank2_and_general_wick_reduction(self):
        for g in xi1_graphs():
            a = reduce_rank2(g['numerator'], len(g['routing']))
            b = reduce_general(g['numerator'], len(g['routing']))
            for key in a:
                self.assertTrue(all(s.expand(x-y) == 0 for x, y in zip(a[key], b[key])), g['id'])

    def test_native_xi1_integrals_match_abe_after_computation(self):
        for q, k, masses in ((np.array([20., 0., 0., 20.]),
                              np.array([10., np.sqrt(2200.), 0., 70.]), (125., 437.)),
                             (np.array([20., 0., 0., 20.]),
                              np.array([-100., np.sqrt(16100.), 0., 130.]), (172., 653.))):
            k2, qk = dot(k, k), dot(q, k)
            vals = [calculate(ms2=m*m, k2=k2, qk=qk, order=40)['finite'] for m in masses]
            # Separate C by the independently verified affine Ms^2 dependence;
            # then separate P using nonzero k^2, rather than imposing P=-B=-3C.
            residual_g = [(v['g']+qk*v['kq'])/2 for v in vals]
            C = -(residual_g[1]-residual_g[0])/(masses[1]**2-masses[0]**2)
            P = (residual_g[0]-C*(k2+2*qk-masses[0]**2))/k2
            refs = source_tensors(q, k, masses[0])['form_factors']
            actual = dict(A=vals[0]['kq']/2, B=vals[0]['kk']/2, C=C, P=P)
            for name in actual:
                self.assertAlmostEqual(actual[name], refs[name], delta=2e-11)

    def test_longitudinal_evaluation_is_not_a_compensator(self):
        # The native code cannot secretly call the literature or required compensator.
        with patch('research.wgamma_d16.algebra.source_tensors', side_effect=AssertionError), \
             patch('research.wgamma_d16.matching.goldstone_projection', side_effect=AssertionError):
            a = calculate(order=24)
            b = calculate_longitudinal(xi=1., order=24)
            for key in a['finite']:
                self.assertAlmostEqual(a['finite'][key], b['finite'][key], delta=2e-8)
            for xi in (.5, 3.):
                c = calculate_longitudinal(xi=xi, order=32)
                self.assertLess(max(abs(x) for x in c['uv_pole'].values()), 1e-8)
                self.assertGreater(abs(c['finite']['kq']-b['finite']['kq']), .1)
                self.assertLess(max(max(g['quadrature_change'].values()) for g in c['graphs']), 1e-6)

    def test_source_bound_st_and_inverse_propagator_terms(self):
        self.assertEqual(scalar_contraction()['residual'], 0)
        p, a = np.array([.8, 2., 3., -1.]), np.array([2., -.1, .7, 4.])
        for xi in (.5, 1., 3.):
            row = contracted_triple(p, a, 80.379**2, xi)
            self.assertLess(row['residual'], 1e-10)
            self.assertGreater(np.max(abs(row['ghost_kernel_remainder'])), 1.)
        st = json.loads((HERE/'st_sources.json').read_text())
        self.assertEqual(len(st['checks']), 16)
        self.assertLess(st['max_abs_residual'], 1e-9)
        for path, expected in st['frozen_source_sha256'].items():
            self.assertEqual(hashlib.sha256((HERE.parents[1]/path).read_bytes()).hexdigest(), expected)
        self.assertEqual(hashlib.sha256((HERE/'extract_st_sources.m').read_bytes()).hexdigest(), st['extraction_sha256'])
        self.assertEqual(hashlib.sha256((HERE/'check_st_sources.py').read_bytes()).hexdigest(), st['validation_sha256'])

    def test_actual_parent_pinch_and_eight_mixed_subloops(self):
        p, _, q = decay_momenta(3., .7)
        r, loop = np.array([.8, 31., -17., 29.]), np.array([1., 2., 3., 4.])
        mw2 = 80.379**2
        self.assertLess(pointwise_pinch_residual(loop, p, q), 1e-12)
        a = calculate_parent(p, q, r, mw2, order=18)
        self.assertLess(a['integral_split_residual'], 1e-15)
        self.assertGreater(np.max(abs(a['pinch'])), 1e-5)
        blocks = calculate_native_parents(p, q, r, mw2, 125.**2, .7, order=12)
        self.assertEqual(len(blocks), 8)
        np.testing.assert_allclose(blocks['WWW'], 2*mw2*a['full'], atol=1e-11, rtol=1e-11)
        self.assertGreater(np.max(abs(blocks['GWW'])), .1)
        native = native_parent_numerator(loop[None, :], p, q, r, mw2, 125**2, .7, ('W',)*3)[0]
        np.testing.assert_allclose(native, 2*mw2*np.array([numerator(mu, loop, p, q) for mu in range(4)]),
                                   atol=1e-8, rtol=1e-13)

    def test_general_xi_parent_finite_contour_and_uncertainty(self):
        p, _, q = decay_momenta(3., .7)
        r, mw2 = np.array([.8, 31., -17., 29.]), 80.379**2
        exact = calculate_parent(p, q, r, mw2, order=16)['full']*2*mw2
        sampled = calculate_parent_rxi(p, q, r, mw2, 125**2, .7, power=11, replicates=4)
        self.assertLess(np.max(abs(exact-sampled['finite'])), 6*np.max(sampled['standard_error'])+1e-4)
        self.assertTrue(np.isfinite(sampled['finite']).all())
        norms = [np.max(abs(exact_parent_integrand([1., 2., 3., 4.], r, p, q, mw2,
                 125.**2, .7, .037+.019j, -.021+.043j, xi=xi))) for xi in (.5, 1., 3.)]
        self.assertGreater(max(norms)-min(norms), 1e-16)
        with self.assertRaisesRegex(ValueError, 'contour'):
            calculate_parent_rxi(p+np.array([200., 0., 0., 0.]), q, r, mw2, 125**2, .7, power=4)

    def test_finite_inner_does_not_release_physical_coefficients(self):
        result = evaluate(example(1))
        self.assertIsNone(result['C_L'])
        self.assertIsNone(result['C_R'])
        self.assertFalse(result['coherent_inclusion'])
        self.assertEqual(result['status'], 'BLOCKED_GAUGE_MATCHING')


if __name__ == '__main__':
    unittest.main()
