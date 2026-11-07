"""Independent rate checks and source guards; only original D12 model cards."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import numpy as np

from research.full_constraints.lfv.validate import (
    HERE, ROOT, OPERATORS, Observable, contact_width, conversion_sign_control,
    group_inventory, original_cards, rate_controls, sha, source_check)


class LFVSourceAndRateTests(unittest.TestCase):
    def test_missing_and_changed_sources_are_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/'source'
            p.write_text('original')
            manifest = {'artifacts': [{'id': 'test', 'path_hint': str(p), 'sha256': sha(p)}]}
            self.assertEqual(source_check(manifest), ['test'])
            p.write_text('changed')
            with self.assertRaisesRegex(ValueError, 'Missing/changed pinned artifact'):
                source_check(manifest)
            manifest['artifacts'][0]['path_hint'] = str(Path(directory)/'absent')
            with self.assertRaises(ValueError):
                source_check(manifest)

    def test_trace_quadrature_and_interference_are_independent_of_polynomial(self):
        coefficients = {k: (i+1)*.07+1j*((i%3)-1)*.13 for i, k in enumerate(OPERATORS)}
        a = contact_width(coefficients, order=12)
        b = contact_width(coefficients, order=20)
        self.assertLess(abs(a/b-1), 3e-14)
        self.assertLess(abs(contact_width({k: c*np.exp(.37j) for k, c in coefficients.items()})/b-1), 3e-14)
        self.assertGreater(abs(b-sum(contact_width({k: c}) for k, c in coefficients.items())), b*.01)

    def test_pinned_unmodified_native_rate_and_original_cards(self):
        if not shutil.which('gfortran'):
            self.skipTest('gfortran absent; native-source replay not performed')
        manifest = json.loads((HERE/'sources.json').read_text())
        source = {r['id']: Path(r['path_hint']) for r in manifest['artifacts']}
        if not source['flavorkit_Lto3Lp'].is_file():
            self.skipTest('Optional pinned external sources absent; no native replay claim')
        source_check(manifest)
        with tempfile.TemporaryDirectory() as directory:
            observable = Observable(source['flavorkit_Lto3Lp'], directory)
            controls = rate_controls(observable)
            cards = original_cards(observable)
            conversion = conversion_sign_control(source['flavorkit_MuEconversion'], directory)
        self.assertLess(max(x['relative_residual'] for x in controls['contact_actions']), 2e-12)
        self.assertEqual(len(cards), 4)
        self.assertTrue(all(x['physical_comparison'] == 'UNKNOWN' and x['exclusion'] is None for x in cards))
        self.assertTrue(all(x['dipole_only_to_tree'] > 1e10 for x in cards))
        self.assertEqual(conversion['status'], 'SOURCE_DISCREPANCY_REPRODUCED')
        au = next(x for x in conversion['records'] if x['target'] == 'Au')
        self.assertAlmostEqual(au['source_over_reference'], 1.0697235742499855, places=12)
        inventory = group_inventory(source['general_2hdm_thdm'])
        for chirality in ('L', 'R'):
            charged = {r['group'] for r in inventory[chirality] if r['charged_mass_dependent']}
            self.assertEqual(charged, {'tHp', 'cHp', 'tauHp', 'kin', 'HA', 'HZ', 'HW'}
                             | ({'1loop'} if chirality == 'L' else set()))
        source_check(manifest)

    def test_research_branch_and_frozen_source_identity(self):
        self.assertEqual(subprocess.check_output(['git', 'branch', '--show-current'],
                         cwd=ROOT, text=True).strip(), 'research/zee-full-constraints')
        parent = '133a34061723b6bb45b19e8ebe29852ac8b5a9c2'
        subprocess.run(['git', 'merge-base', '--is-ancestor', parent, 'HEAD'], cwd=ROOT, check=True)
        for name in ('module3/core.py', 'module3/tree.py', 'module4/amplitudes.py',
                     'module4/charged_scalar.py', 'module4/interface.py'):
            self.assertEqual((ROOT/name).read_bytes(), subprocess.check_output(
                ['git', 'show', parent+':'+name], cwd=ROOT))

    def test_saved_receipt_preserves_physics_blocks_and_source_identity(self):
        receipt = json.loads((HERE.parent/'LFV_VALIDATION.json').read_text())
        self.assertEqual(receipt['status'], 'LFV_FULL_COVERAGE_BLOCKED')
        self.assertEqual(receipt['physical_lfv'], 'UNKNOWN')
        self.assertFalse(receipt['scoped_observable_validated'])
        self.assertIsNone(receipt['exclusion'])
        self.assertIsNone(receipt['global_acceptance'])
        self.assertEqual(receipt['added_amplitudes'], [])
        self.assertEqual(receipt['new_model_cards'], 0)
        self.assertEqual(receipt['native_spectrum_runs'], 0)
        self.assertEqual(receipt['manifest_sha256'], sha(HERE/'sources.json'))
        self.assertEqual(receipt['code_sha256'], sha(HERE/'validate.py'))
        self.assertEqual(receipt['experimental_snapshot_sha256'], sha(HERE/'experiments.json'))
        cards = json.loads((ROOT/'validation/module12/d12_benchmarks.json').read_text())['groups']
        self.assertEqual([x['scalar_sha256'] for x in receipt['original_D12_cards']],
                         [x['scalar_sha256'] for x in cards])
        self.assertEqual([x['module4_output_sha256'] for x in receipt['original_D12_cards']],
                         [x['witnesses']['central']['module4_output_sha256'] for x in cards])
        matrix = json.loads((HERE.parent/'VALIDATION_MATRIX.json').read_text())
        self.assertEqual(matrix['LFV']['status'], receipt['status'])
        self.assertEqual(matrix['B_to_Xs_gamma']['feasibility_gate'], 'B_FULL_RATE_BLOCKED')
        self.assertIsNone(matrix['global_acceptance'])


if __name__ == '__main__':
    unittest.main()
