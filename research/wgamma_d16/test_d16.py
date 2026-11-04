"""Scoped tests of actual reductions and explicit incompleteness; no full suite."""
import copy
import hashlib
import json
import math
import re
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np

from module3.core import vertices
from module4.matching_audit import w_source_decomposition
from .algebra import (ETA, ID, METRIC, angular_projection, abe_A_double_integral,
                      bar, corrected_abe_B8_photon, decay_momenta, dot,
                      outer_current, projected_source_check, reference_kernels,
                      slash, source_tensors, spinor, w_propagator)
from .inventory import inner_diagrams, missing_contributions, require_complete, require_gauge_independence
from .matching import HERE, ROOT, conditional_source_A, decode_matrix, evaluate, example, gauge_falsifier
from .symbolic_reductions import reductions


class D16Tests(unittest.TestCase):
    def test_exact_unequal_mass_B_two_attachments(self):
        for mi, mj in ((3., .7), (.1056583755, .00051099895), (1.77686, .1056583755)):
            pi, pj, q = decay_momenta(mi, mj)
            self.assertLess(abs(dot(q, q)), 2e-15)
            for si in range(2):
                self.assertLess(np.max(abs((slash(pi)-mi*ID)@spinor(pi, mi, si))), 2e-15)
                for sj in range(2):
                    for k in (np.array([.3, .8, -.5, 1.1]), np.array([-.2, 1.2, .7, -.6])):
                        args = (pi, pj, k, mi, mj, .037+.019j, -.021+.043j, si, sj)
                        current = outer_current(*args)
                        one = outer_current(*args, attachment='daughter')
                        self.assertLess(abs(dot(k, current)), 3e-15)
                        if si == 0 and sj == 0:
                            self.assertGreater(abs(dot(k, one)), 1e-6)

    def test_full_source_tensor_reductions_and_ward_falsifiers(self):
        for delta, masses in ((.73, (125., 437.)), (-.29, (172., 653.))):
            result = projected_source_check(delta=delta, masses=masses)
            for name in ('B', 'C_sum', 'P_plus_pinch', 'full_minus_A',
                         'real_photon_Ward', 'virtual_photon_Ward'):
                self.assertLess(result[name], 2e-15, (name, result))
            self.assertGreater(result['bare_real_photon_Ward'], 1e-5)
            self.assertGreater(result['omitted_H_C_remainder'], 1e-3)
        q, k = np.array([1., 0., 0., 1.]), np.array([.4, 2., -.3, 3.])
        a = source_tensors(q, k, 437., order=24)
        b = source_tensors(q, k, 437., order=48)
        for name in ('A', 'P', 'B', 'C', 'pinch'):
            np.testing.assert_allclose(a[name], b[name], rtol=3e-14, atol=2e-10)
        self.assertLess(angular_projection(), 3e-17)

    def test_exact_mixing_and_diagonal_exception(self):
        self.assertEqual(reductions()['status'], 'PASS')
        inp = example(1)
        p = inp['physical']
        ml = np.array(inp['lepton_masses_GeV'])
        D = decode_matrix(inp['D'])
        Cs = vertices(D, p, ml)
        delta = p['beta']-p['alpha']
        neutral_sum = math.cos(delta)*Cs['h'][0]+math.sin(delta)*Cs['H'][0]
        np.testing.assert_allclose(neutral_sum, np.diag(ml/p['v']), atol=8e-18)
        # The full scalar diagonal sum is NOT zero: Abe's EDM axial sum rule
        # cannot be silently reused for the entire magnetic moment.
        self.assertGreater(abs(neutral_sum[1, 1]), 1e-4)

    def test_native_extraction_source_bound(self):
        evidence = json.loads((HERE/'native_vertices.json').read_text())
        self.assertEqual(evidence['coefficient_validation']['status'], 'PASS')
        self.assertEqual(evidence['coefficient_validation']['check_count'], 444)
        self.assertLess(evidence['coefficient_validation']['max_abs_residual'], 1e-8)
        for path, expected in evidence['frozen_source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), expected, path)
        for path, expected in evidence['driver_sha256'].items():
            self.assertEqual(hashlib.sha256((HERE/path).read_bytes()).hexdigest(), expected, path)
        self.assertIn('RXi[Wm]', evidence['raw']['sGhost_{1, gWm}'])
        self.assertIn('sPhotonWG_{2, 2}', evidence['raw'])
        self.assertIn('Hlepton_{3, 2, 1}', evidence['raw'])
        self.assertIn('ZA[2, 1]*ZP[1, 1] + ZA[2, 2]*ZP[1, 2]', evidence['raw']['AWG_1'])
        self.assertIn('{0, 1}', evidence['raw']['AWW'])
        self.assertIn('{0, 1}', evidence['raw']['AGG'])
        self.assertEqual(evidence['topology_crosscheck']['classes_amplitudes'], len(inner_diagrams()))

    def test_conditional_kernels_independent_integrals_and_erratum(self):
        for z in (.013, .413, 2.7):
            refs = reference_kernels(z)
            old = w_source_decomposition(z)
            for ours, frozen in [('CHK', 'CHK'), ('Ilisie', 'Ilisie'), ('Abe_A', 'Abe_transverse')]:
                self.assertAlmostEqual(refs[ours], old[frozen], delta=1e-9)
            self.assertAlmostEqual(abe_A_double_integral(z), refs['Abe_A'], delta=1e-9)
            self.assertAlmostEqual(corrected_abe_B8_photon(z)/2, refs['Abe_A'], delta=1e-9)
            self.assertAlmostEqual(refs['CHK']-refs['Abe_A'], .75*(refs['g']+refs['h']), delta=1e-13)
            self.assertAlmostEqual(refs['Ilisie']-refs['Abe_A'], 1.5*(3*refs['f']-2*refs['g']), delta=1e-13)
        self.assertGreater(abs(reference_kernels(.413)['CHK']-reference_kernels(.413)['Abe_A']), .2)

    def test_conditional_complex_chiral_rephase_and_physical_nulls(self):
        for index in (0, 1):
            inp = example(index)
            a, _ = conditional_source_A(inp)
            b, _ = conditional_source_A(inp, method='double-integral')
            np.testing.assert_allclose(a, b, rtol=3e-10, atol=1e-23)
            self.assertTrue(np.all(abs(a.real) > 1e-12) and np.all(abs(a.imag) > 1e-12))
            inp2 = copy.deepcopy(inp)
            D = decode_matrix(inp['D'])
            P = np.diag(np.exp(1j*np.array([.27, -.39, .84])))
            D2 = P.conjugate()@D@P
            inp2['D'] = np.stack([D2.real, D2.imag], axis=-1).tolist()
            transformed, _ = conditional_source_A(inp2)
            phase = P[inp['j'], inp['j']].conjugate()*P[inp['i'], inp['i']]
            np.testing.assert_allclose(transformed, phase*a, rtol=2e-14)
            inp2 = copy.deepcopy(inp)
            inp2['physical']['mh2'] = inp2['physical']['mh1']
            zero, _ = conditional_source_A(inp2)
            self.assertLess(np.max(abs(zero)), 2e-23)
            inp2['physical']['alpha'] = inp2['physical']['beta']
            zero, _ = conditional_source_A(inp2)
            self.assertEqual(np.max(abs(zero)), 0)

    def test_Rxi_propagator_requires_more_than_mass_replacement(self):
        k, mw = np.array([.4, 2., -.3, 3.]), 80.379
        k2 = dot(k, k)
        unitary = -1j/(k2-mw*mw)*(METRIC-np.outer(k, k)/mw**2)
        for xi in (.5, 1., 3.):
            expected = unitary-1j*np.outer(k, k)/(mw*mw*(k2-xi*mw*mw))
            np.testing.assert_allclose(w_propagator(k, mw, xi), expected, atol=3e-20, rtol=2e-14)
        for index in (0, 1):
            falsifier = gauge_falsifier(example(index))
            self.assertEqual(falsifier['status'], 'FAIL')
            self.assertGreater(falsifier['max_relative_xi_variation'], .04)
            self.assertEqual(falsifier['complete_projected_Rxi']['status'], 'NOT_EVALUATED')

    def test_missing_graph_or_pinch_cannot_be_a_zero(self):
        ids = missing_contributions()
        self.assertEqual(len(inner_diagrams()), 26)
        self.assertEqual(len(set(ids)), len(ids))
        contributions = {name: 1+2j for name in ids}
        for missing in ('bubble_W', 'triangle_WGG_+1', 'P_longitudinal_xi', 'P_Zee_completion'):
            incomplete = dict(contributions)
            del incomplete[missing]
            with self.assertRaisesRegex(RuntimeError, re.escape(missing)):
                require_complete(incomplete)
            incomplete[missing] = None
            with self.assertRaises(RuntimeError):
                require_complete(incomplete)

    def test_gauge_acceptance_rejects_incomplete_or_dependent_data(self):
        with self.assertRaises(RuntimeError):
            require_gauge_independence({1.: [1j, 2j]})
        with self.assertRaises(RuntimeError):
            require_gauge_independence({.5: [1j, 2j], 1.: [1j, 2j], 3.: [1.01j, 2j]})
        with self.assertRaises(ValueError):
            require_gauge_independence({.5: [float('nan'), 2j], 1.: [1j, 2j], 3.: [1j, 2j]})
        with self.assertRaises(ValueError):
            require_gauge_independence({.5: [None, None], 1.: [None, None], 3.: [None, None]})

    def test_physical_interface_stays_blocked(self):
        result = evaluate(example(1))
        self.assertEqual(result['status'], 'BLOCKED_GAUGE_MATCHING')
        self.assertIsNone(result['C_L'])
        self.assertIsNone(result['C_R'])
        self.assertFalse(result['coherent_inclusion'])
        self.assertFalse(result['conditional_source_A']['accepted_for_physics'])
        self.assertEqual(result['known_physical_zeros']['A_pure_W_G_sector']['status'], 'NOT_APPLICABLE')
        run = subprocess.run([sys.executable, '-m', 'research.wgamma_d16.matching',
                              '--require-pass'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)['status'], 'BLOCKED_GAUGE_MATCHING')


if __name__ == '__main__':
    unittest.main()
