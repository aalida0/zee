"""D1 falsification controls plus independent checks of committed real evidence."""
import copy
import json
from pathlib import Path
import unittest

from module2.interface import canonical_hash, evaluate as neutrino_evaluate
from module6.coherent_pilot import SOURCE_TOP_MS_160, LHA_SOURCE_SHA256
from module6.d1_family_grid import generate
from module6.d1_run_grid import matching_provenance, validate_row, scoped, comparisons

ROOT = Path(__file__).resolve().parents[1]


def grid():
    return generate(json.loads((ROOT/'module3/example.json').read_text()))[0]


class RunnerControls(unittest.TestCase):
    def test_stale_changed_charged_masses(self):
        for key in ('mH1', 'mH2'):
            row = grid()[0]
            row['module2_input']['scalar']['record']['physical'][key] += 1
            with self.subTest(key=key), self.assertRaises(ValueError): validate_row(row)

    def test_swapped_ids_even_with_rehash(self):
        rows = grid()
        rows[0]['module2_input']['scalar'] = rows[1]['module2_input']['scalar']
        with self.assertRaises(ValueError): validate_row(rows[0])

    def test_exact_matching_source_required(self):
        matching_provenance(160., SOURCE_TOP_MS_160, LHA_SOURCE_SHA256)
        for mu, mt, lha in ((170., SOURCE_TOP_MS_160, LHA_SOURCE_SHA256),
                            (160., 163., LHA_SOURCE_SHA256), (160., SOURCE_TOP_MS_160, '0'*64),
                            (True, SOURCE_TOP_MS_160, LHA_SOURCE_SHA256),
                            (160., float('inf'), LHA_SOURCE_SHA256)):
            with self.subTest(mu=mu, mt=mt), self.assertRaises(ValueError): matching_provenance(mu, mt, lha)

    def test_original_target_and_real_inverse_closure_all_six(self):
        rows = grid()
        for row in rows:
            self.assertEqual(row['module2_input']['target_eV'], rows[0]['module2_input']['target_eV'])
            out = neutrino_evaluate(row['module2_input'])
            self.assertLess(out['inverse']['family_relative_residual'], 2e-9)
            self.assertEqual(out['gates']['data_comparison'], 'NOT_EVALUATED')

    def test_invariance_falsification(self):
        base = dict(execution_status='PASS_SCOPED', spectrum_name='source_spectrum', family_name='a',
                    delta_C7=-.06, delta_C8=-.06, conditional_linear_value_1e_minus4=4.,
                    radiative_subset_BR={'mu_to_e_gamma': 1e-19})
        changed = dict(base, family_name='b', delta_C7=-.07)
        with self.assertRaises(ValueError): comparisons([base, changed])
        changed['delta_C7'] = base['delta_C7']
        self.assertEqual(comparisons([base, changed])['fixed_spectrum']['source_spectrum']['flavor_max_minus_min']['delta_C7'], 0.)

    def test_missing_sectors_fail_closed(self):
        with self.assertRaises(KeyError): scoped({'status': 'COHERENT_ZEE_CANDIDATE_DIAGNOSTIC_ONLY'})


class RealEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads((ROOT/'validation/module6/d1_family_scan.json').read_text())

    def test_six_actual_outputs_and_bound_hashes(self):
        evidence = self.evidence
        self.assertEqual(evidence['real_points_executed'], 6)
        self.assertEqual(evidence['status'], 'D1_REAL_GRID_EXECUTED_NOT_PHYSICAL_ACCEPTANCE')
        rows = grid()
        for row, point in zip(rows, evidence['points']):
            self.assertEqual(point['execution_status'], 'PASS_SCOPED')
            self.assertEqual(point['input_sha256'], canonical_hash(row))
            self.assertEqual(point['bound_scalar_sha256'], canonical_hash(row['module2_input']['scalar']['record']))
            self.assertLess(point['target_vs_reconstructed_relative_error'], 2e-9)
            self.assertIsNone(point['global_zee_acceptance'])
            self.assertFalse(point['COMPLETE_LFV'])
            self.assertEqual(point['lfv_gates']['full_lfv'], 'NOT_EVALUATED')
            self.assertEqual(point['neutrino_gates']['data_comparison'], 'NOT_EVALUATED')

    def test_regression_and_fixed_spectrum_invariance(self):
        self.assertEqual(len(self.evidence['D0_regression']), 4)
        self.assertTrue(all(x['matches'] for x in self.evidence['D0_regression'].values()))
        comparison = comparisons(self.evidence['points'])
        self.assertEqual(comparison, self.evidence['comparisons'])
        for group in comparison['fixed_spectrum'].values():
            self.assertEqual(group['points'], 3)
            self.assertTrue(all(abs(x)<1e-13 for x in group['flavor_max_minus_min'].values()))

    def test_unexpected_acceptance_and_nonfinite_rejected(self):
        # Use real local outputs when present; compact evidence remains portable.
        path = ROOT/self.evidence['points'][0]['output_path']
        if not path.exists():
            self.skipTest('Ignored full real output unavailable; compact evidence checked separately')
        result = json.loads(path.read_text())['pilot']
        scoped(result)
        for mutation in ('global', 'full', 'data', 'missing', 'excluded', 'nan'):
            x = copy.deepcopy(result)
            if mutation == 'global': x['global_zee_acceptance'] = True
            if mutation == 'full': x['neutrino_lfv']['COMPLETE_LFV'] = True
            if mutation == 'data': x['neutrino']['gates']['data_comparison'] = 'PASS'
            if mutation == 'missing': del x['neutrino_lfv']['module4_Barr_Zee_and_W_completion']
            if mutation == 'excluded': x['bsgamma']['flavor_classification'] = 'EXCLUDED'
            if mutation == 'nan': x['bsgamma']['delta_C7'] = float('nan')
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, KeyError)): scoped(x)


if __name__ == '__main__': unittest.main()
