import copy
import json
import math
import unittest

import numpy as np

from module11.d11b_offline_fit import (
    ROOT, SOURCE, SOURCE_SHA256, BENCHMARKS, ML, YUKAWAS, TARGET_LABEL,
    PROPOSAL_LABEL, check_target, counterexamples, execute, file_hash,
    inverse_input, load_source, loop_inputs, marginal_contains, perturbativity,
    phase_error, scalar_records, target, target_specs,
)
from module2.core import forward, NumericalUnknown
from module2.interface import canonical_hash, decode, encode, evaluate
from module2.observables import observables


class D11BOfflineTests(unittest.TestCase):
    def test_pinned_source_and_full_scalar_hashes(self):
        self.assertEqual(file_hash(SOURCE), SOURCE_SHA256)
        self.assertEqual(load_source()['original_analysis_variant'], 'IC24_with_SK_atm')
        scalars, statuses = scalar_records()
        expected = ('ff0c551534e5051f223c00435293403e3b553f52e0cbec4344287da8b3dce862',
                    '9117e7af53f9ad5c21f964a7c216de7af5824e903856fed54b9b237c922f4a1d')
        for name, digest in zip(BENCHMARKS, expected):
            self.assertEqual(scalars[name]['sha256'], digest)
            self.assertEqual(canonical_hash(scalars[name]['record']), digest)
            self.assertEqual(statuses[name], 'D10_GLOBAL_CERTIFIED')
        for name in ('P2_beta_shift', 'F13_heavy_0000981', 'F13_heavy_0001003'):
            self.assertEqual(statuses[name], 'D10_UNKNOWN')

    def test_all_targets_independent_takagi_and_phases(self):
        for ordering in ('NO', 'IO'):
            for s in target_specs(ordering):
                M, masses, U, p = target(ordering, s['lightest_eV'], s['alpha21_rad'], s['alpha31_rad'], s['parameters'])
                checks = check_target(M, masses, U, ordering, p, s['alpha21_rad'], s['alpha31_rad'])
                self.assertLess(max(checks.values()), 2e-10)
                self.assertLess(np.linalg.norm(M-M.T), 1e-16)
                self.assertGreater(np.linalg.norm(M-M.conj().T), 1e-3)
                K = M.conj().T@M
                self.assertLess(np.linalg.norm(K-K.conj().T), 1e-17)

    def test_signed_io_splitting_and_mass_labels(self):
        for ordering in ('NO', 'IO'):
            M, m, U, p = target(ordering, .01, .7, 2.1)
            self.assertAlmostEqual(m[0 if ordering == 'NO' else 2], .01, places=15)
            self.assertAlmostEqual(m[1]**2-m[0]**2, p['dm21_eV2'], places=17)
            self.assertAlmostEqual(m[2]**2-m[0 if ordering == 'NO' else 1]**2, p['dm3ell_eV2'], places=17)
            wrong = dict(p, dm3ell_eV2=-p['dm3ell_eV2'])
            with self.assertRaises(ValueError):
                target(ordering, .01, .7, 2.1, wrong)
            with self.assertRaises(ValueError):
                target(ordering, .01, .7, 2.1, dict(p, dm21_eV2=-p['dm21_eV2']))

    def test_continuous_cyclic_delta_and_majorana_boundaries(self):
        p = target('NO', .01, .7, 2.1)[3]
        for value in (0., 1e-9, 2-1e-9, 2., 2.03):
            params = dict(p, deltaCP_over_pi=value)
            M, m, U, _ = target('NO', .01, .7, 2.1, params)
            other = target('NO', .01, .7+2*math.pi, 2.1+2*math.pi, dict(params, deltaCP_over_pi=value+2))[0]
            self.assertLess(np.linalg.norm(other-M), 1e-15)
            self.assertLess(phase_error(observables(M, 'NO')['delta_rad'], math.pi*value), 1e-10)
        self.assertTrue(marginal_contains(.02, [.7, 2.03], 2))
        self.assertTrue(marginal_contains(2.02, [.7, 2.03], 2))
        self.assertFalse(marginal_contains(.2, [.7, 2.03], 2))
        left = target('NO', .01, .7, 2.1, dict(p, deltaCP_over_pi=2-1e-9))[0]
        right = target('NO', .01, .7, 2.1, dict(p, deltaCP_over_pi=1e-9))[0]
        self.assertLess(np.linalg.norm(right-left), 1e-9)

    def test_only_single_coordinate_sensitivity(self):
        for ordering in ('NO', 'IO'):
            specs = target_specs(ordering)
            self.assertEqual(len(specs), 21)
            p = specs[0]['parameters']
            self.assertEqual(sum(s['label'] == TARGET_LABEL for s in specs), 9)
            for s in specs[9:]:
                self.assertEqual(s['label'], PROPOSAL_LABEL)
                changed = [k for k in p if p[k] != s['parameters'][k]]
                self.assertEqual(changed, [s['varied_parameter']])

    def test_actual_inverse_family_forward_and_yukawa_rotation(self):
        scalars, _ = scalar_records()
        cone = dict(t=dict(real=.25, imag=.1), scale=.001, root=0, chart=[0, 1, 2], phase_rad=.43)
        for scalar in scalars.values():
            for ordering in ('NO', 'IO'):
                for index in (0, 4, 8):
                    inp = inverse_input(scalar, ordering, target_specs(ordering)[index], cone,
                                        [1e-4+2e-5j, -2e-4j, 3e-4, -.5e-4+1e-4j])
                    metrics, out = execute(inp)
                    self.assertEqual((metrics['rank'], metrics['nullity_complex']), (5, 4))
                    self.assertLess(metrics['closure_relative'], 2e-9)
                    self.assertTrue(metrics['selection']['below_one'])
                    F, D, Ye, Ye2 = (decode(out[k]) for k in YUKAWAS)
                    self.assertLess(np.linalg.norm(F+F.T), 1e-16)
                    self.assertLess(np.linalg.norm(forward(F, D, **loop_inputs(scalar))-decode(inp['target_eV'])), 1e-10)
                    p = scalar['record']['physical']
                    c, s = math.cos(p['beta']), math.sin(p['beta'])
                    self.assertLess(np.linalg.norm(c*Ye+s*Ye2-np.diag(np.sqrt(2)*ML/p['v'])), 1e-16)
                    self.assertLess(np.linalg.norm(-s*Ye+c*Ye2-D), 1e-16)
                    self.assertEqual(out['comparison']['status'], 'NOT_EVALUATED')
                    self.assertIsNone(out['global_zee_acceptance'])

    def test_all_four_yukawas_and_strict_thresholds(self):
        out = {k: encode(np.zeros((3, 3), complex)) for k in YUKAWAS}
        for k in YUKAWAS:
            bad = copy.deepcopy(out)
            A = np.zeros((3, 3), complex)
            A[0, 1] = 1.
            bad[k] = encode(A)
            self.assertFalse(perturbativity(bad)['below_one'])
            self.assertTrue(perturbativity(bad)['below_sqrt4pi'])
            A[0, 1] = math.sqrt(4*math.pi)
            bad[k] = encode(A)
            self.assertFalse(perturbativity(bad)['below_sqrt4pi'])

    def test_singular_closure_and_statistical_flags_fail_closed(self):
        scalar = scalar_records()[0][BENCHMARKS[0]]
        records = counterexamples(scalar)
        self.assertEqual(len(records), 7)
        self.assertTrue(all(r['rejected'] for r in records))
        self.assertIn('forward closure', records[3]['error'])
        p = target('IO', .01, .7, 2.1)[3]
        with self.assertRaises(ValueError):
            target('IO', .01, .7, 2.1, dict(p, joint_3sigma_acceptance=True))

    def test_executed_evidence_and_replay_witnesses(self):
        r = json.loads((ROOT/'validation/module11/d11b_offline_fit.json').read_text())
        self.assertIsNone(r['global_zee_acceptance'])
        self.assertIsNone(r['oscillation_chi2'])
        self.assertFalse(r['COMPLETE_LFV'])
        self.assertEqual(len(r['groups']), 4)
        for p, digest in r['source_sha256'].items():
            self.assertEqual(file_hash(p), digest, p)
        for g in r['groups']:
            self.assertEqual(g['attempted'], g['closed']+len(g['failures']))
            self.assertTrue(all(t['below_one'] > 0 for t in g['per_target']))
            for witness in g['witnesses'].values():
                metrics, out = execute(witness['input'])
                self.assertEqual(metrics['input_sha256'], witness['metrics']['input_sha256'])
                self.assertLess(metrics['closure_relative'], 2e-9)
                for k in YUKAWAS:
                    np.testing.assert_allclose(decode(out[k]), decode(witness['Yukawas'][k]), rtol=1e-10, atol=1e-14)


if __name__ == '__main__':
    unittest.main()
