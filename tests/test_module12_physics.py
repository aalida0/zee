"""Numerical, source-linked D12 checks. No historical guard is disabled."""
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np

from module12.study import ROOT, OUTPUT, evaluate_case, module3_input, decays
from module11.d11b_offline_fit import scalar_records, execute, file_hash
from module2.interface import canonical_hash, decode
from module3.core import radiative_width
from module4.interface import evaluate as lfv4


class D12Physics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(OUTPUT.read_text())
        cls.groups = cls.report['groups']

    def test_01_source_identity_and_certificates(self):
        for path, digest in self.report['source_sha256'].items():
            self.assertEqual(file_hash(path), digest, path)
        scalars, statuses = scalar_records()
        self.assertEqual(len(scalars), 2)
        for g in self.groups:
            self.assertEqual(g['scalar_sha256'], scalars[g['scalar']]['sha256'])
        for name in ('P2_beta_shift', 'F13_heavy_0000981', 'F13_heavy_0001003'):
            self.assertEqual(statuses[name], 'D10_UNKNOWN')

    def test_02_exact_D11B_central_and_actual_inverse(self):
        previous = json.loads((ROOT/'validation/module11/d11b_offline_fit.json').read_text())
        for g in self.groups:
            r = g['witnesses']['central']
            old = next(x for x in previous['groups'] if x['benchmark_id'] == g['scalar'] and x['ordering'] == g['ordering'])['witnesses']['reference_bestfit']
            self.assertEqual(canonical_hash(r['module2_input']), old['metrics']['input_sha256'])
            metrics, nout = execute(r['module2_input'])
            self.assertEqual(canonical_hash(nout), r['module2_output_sha256'])
            for key in ('F', 'D', 'Ye', 'Ye2'):
                self.assertEqual(nout[key], old['Yukawas'][key])
            self.assertLess(metrics['closure_relative'], 2e-9)

    def test_03_all_136_closed_perturbative_and_source_ids(self):
        total = 0
        for g in self.groups:
            self.assertEqual(len(g['family']), 28)
            self.assertEqual(len({r['id'] for r in g['family']}), 28)
            for r in g['family']+g['texture_sensitivity']:
                self.assertLess(r['metrics']['closure_relative'], 2e-9)
                self.assertLess(r['metrics']['selection']['overall_max'], 1.)
                self.assertEqual(r['metrics']['rank'], 5)
                self.assertEqual(r['metrics']['nullity_complex'], 4)
                total += 1
        self.assertEqual(total, 136)

    def test_04_signed_coherent_amplitudes_not_double_counted(self):
        g = self.groups[0]
        row = g['witnesses']['central']
        inp = row['module2_input']
        _, nout = execute(inp)
        data3 = module3_input(inp)
        extra = json.loads((ROOT/'module4/example.json').read_text())['two_loop_inputs']
        out = lfv4(dict(schema_version='1.0.0', kind='module3_matching_input_v1',
                        module3_input=data3, module2_output=nout, two_loop_inputs=extra))
        for name, channel in out['channels'].items():
            pairs = np.array([[complex(**r[k]) for k in ('C_L', 'C_R')] for r in channel['ledger'].values()])
            self.assertFalse(any('W_gamma' in key for key in channel['ledger']))
            self.assertEqual(len([k for k in channel['ledger'] if k.startswith('module3_')]), 7)
            self.assertTrue(any(k.endswith('_scalar_gamma') for k in channel['ledger']))
            total = pairs.sum(axis=0)
            np.testing.assert_allclose(total, [complex(**channel[k]) for k in ('C_L', 'C_R')], rtol=1e-13, atol=1e-30)
            stored = row['signed_radiative'][name]
            self.assertAlmostEqual((sum(stored['grouped_BR'].values())+
                                  sum(r['signed_BR'] for r in stored['interference']))/stored['BR_implemented'], 1., places=11)
            self.assertEqual(channel['partial_BR'], row['radiative'][name])

    def test_05_two_contraction_tree_and_full_interface_replay(self):
        row = self.groups[2]['witnesses']['low_joint']
        replay = evaluate_case(row['module2_input'], full_tree=True)
        self.assertEqual(replay['mu_to_3e_tree'], row['mu_to_3e_tree'])
        self.assertEqual(replay['tree_observables'], row['tree_observables'])
        self.assertLess(replay['tree_quadrature_relative_change'], 2e-5)
        for item in replay['tree_observables'].values():
            self.assertEqual(item['physical_status'], 'TREE_SUBSET_ONLY')
            self.assertEqual(item['status'], 'PASS')

    def test_06_exact_D10_cascade_width_and_27_channel_totals(self):
        for g in self.groups[::2]:
            row = g['witnesses']['central']
            inp = row['module2_input']
            _, nout = execute(inp)
            actual = decays(inp, nout)
            p = inp['scalar']['record']['physical']
            m1, m2, mz = p['mH1'], p['mH2'], inp['scalar']['record']['electroweak']['mZ']
            # Independent closed-form gauge width from the derivative vertex
            # and massive-vector polarization sum, not a D4 historical number.
            lam = (m2*m2-(m1+mz)**2)*(m2*m2-(m1-mz)**2)
            expected = math.sin(2*p['gamma'])**2*lam**1.5/(64*math.pi*p['v']**2*m2**3)
            width = next(r['width_GeV'] for r in actual['H2']['channels'] if r['channel'] == 'H1 Z')
            self.assertAlmostEqual(width/expected, 1., places=12)
            for k in ('H1', 'H2'):
                self.assertEqual(len(actual[k]['channels']), 27)
                self.assertAlmostEqual(sum(actual[k]['total']['branching_fractions'].values()), 1., places=13)
                self.assertEqual(actual[k]['total'], row['decays'][k]['total'])

    def test_07_texture_suppression_and_measured_local_sensitivity(self):
        for g in self.groups:
            central, low = (g['witnesses'][k] for k in ('central', 'low_joint'))
            _, nout = execute(low['module2_input'])
            d = decode(nout['D'])
            self.assertLess(max(abs(d[0, 1]), abs(d[1, 0])), 1e-15)
            self.assertLess(low['radiative']['mu_to_e_gamma'], central['radiative']['mu_to_e_gamma']*1e-6)
            self.assertLess(low['mu_to_3e_tree'], central['mu_to_3e_tree']*1e-12)
            self.assertLess(abs(low['cascade_product']/central['cascade_product']-1), .001)
            # The tested 0.001 texture neighborhood also reduces both subsets.
            for r in g['texture_sensitivity']:
                if r['base_design'] == 'texture_0.001':
                    self.assertLess(r['radiative']['mu_to_e_gamma'], 1.5e-13)
                    self.assertLess(r['mu_to_3e_tree'], 1e-12)

    def test_08_BMU_source_matching_and_Yukawa_factorization(self):
        sys.path.insert(0, str(ROOT/'scripts'))
        from zee_module5_bmu_nlo import matching
        b = self.report['B_to_Xs_gamma']
        self.assertEqual(b['status'], 'EXECUTED_SOURCE_VERIFIED_D9B_LEGACY_NLO')
        for g in self.groups:
            row = b['rows'][g['scalar']]
            self.assertEqual(row['family_repeat_absolute_difference'], 0.)
            for mass, part in zip(row['masses_GeV'], row['ordinary_parts']):
                self.assertEqual(matching(mass, row['tanbeta'], b['baseline']['mt_match'], mu=160., flip=False), part)
            for w in g['witnesses'].values():
                self.assertEqual(w['BR_B_Xs_gamma_legacy_NLO'], row['BR_legacy_NLO'])
                self.assertEqual(w['scalar_sha256'], row['scalar_sha256'])

    @unittest.skipUnless((ROOT/'validation/module12/local/superiso/rate_probe').exists(),
                         'Reconstruct the official archive + D9B patch to run the live backend check')
    def test_09_live_source_verified_superiso(self):
        b = self.report['B_to_Xs_gamma']
        self.assertEqual(file_hash('validation/module12/local/superiso/rate_probe'), b['binary_sha256'])
        for row in b['rows'].values():
            raw = subprocess.check_output(row['command'], text=True)
            output = {k: float(v) for k, v in (s.split() for s in raw.splitlines())}
            self.assertEqual(output['injected_BR'], row['BR_legacy_NLO'])
            self.assertEqual(output['injected_BR'], output['metadata_BR'])
            self.assertEqual(output['injected_P2'], 0.)

    def test_10_no_full_flavor_or_unexecuted_collider_claim(self):
        self.assertFalse(self.report['COMPLETE_LFV'])
        self.assertFalse(self.report['2026_GLOBAL_FLAVOR_FILTER_READY'])
        self.assertIsNone(self.report['global_zee_acceptance'])
        self.assertIsNone(self.report['mass_exclusion'])
        self.assertEqual(self.report['production']['status'], 'NOT_EXECUTED')
        self.assertIsNone(self.report['production']['sigma_13p6_TeV_pb'])
        self.assertIsNone(self.report['production']['sigma_14_TeV_pb'])
        bad = copy.deepcopy(self.groups[0]['witnesses']['central']['module2_input'])
        bad['scalar']['record']['physical']['mH2'] += 1.
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            execute(bad)


if __name__ == '__main__':
    unittest.main()
