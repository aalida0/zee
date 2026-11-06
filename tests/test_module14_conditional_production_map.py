import copy
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from module14.scan import digest, file_sha
from module14.conditional_scan.candidate_export import BASE, CERTIFIED, shortlist
from module14.conditional_scan.production_map_run import MAP_IDS, REMAINING_IDS, BENCHMARK_IDS, LOCAL, WORK
from module14.conditional_scan.production_map_validate import validate_one, validate_run_card
from module14.conditional_scan.production_map_export import export, ratio
from module14.conditional_scan.workflow import load


class MapTests(unittest.TestCase):
    def test_finite_scope_derived_from_original_sample(self):
        groups, _ = shortlist(load(BASE/'remote_conditional_summary.json'))
        self.assertEqual(set(MAP_IDS), set(groups[CERTIFIED]))
        self.assertEqual(len(REMAINING_IDS), 13)
        self.assertEqual(set(REMAINING_IDS) & set(BENCHMARK_IDS), set())

    def test_actual_energy_not_relabelling_and_pdf_scale_falsifiers(self):
        mass = 1035.7
        raw = """1 = lpp1
1 = lpp2
6500 = ebeam1
6500 = ebeam2
1035.7 = scale
1035.7 = dsqrt_q2fact1
1035.7 = dsqrt_q2fact2
263000 = lhaid
0 = ptheavy
0 = dsqrt_shat
-1 = dsqrt_shatmax
'lhapdf' = pdlabel
.true. = fixed_ren_scale
.true. = fixed_fac_scale
False = use_syst
'none' = systematics_program
5000 = nevents
"""
        validate_run_card(raw, mass, 13)
        with self.assertRaisesRegex(ValueError, 'ebeam'):
            validate_run_card(raw, mass, 14)
        from module8.run_capture import set_card
        new = set_card(raw, {'ebeam1': 7000., 'ebeam2': 7000.})
        validate_run_card(new, mass, 14)
        for field, value in [('ebeam2', 6500), ('scale', 700), ('lhaid', 1), ('ptheavy', 20)]:
            with self.assertRaises(ValueError):
                validate_run_card(set_card(new, {field: value}), mass, 14)

    def test_measured_ratio_uncertainty(self):
        a = {'sigma_pb': 2., 'integration_error_pb': .02}
        b = {'sigma_pb': 1., 'integration_error_pb': .01}
        value, error = ratio(a, b)
        self.assertEqual(value, 2.)
        self.assertAlmostEqual(error, 2*math.sqrt(2)*.01)

    def test_export_missing_values_stay_null_and_bytes_deterministic(self):
        rows = [{'id': 1, 'ordering': 'NO', 'family': 0, 'energy_TeV': energy, 'rank_at_energy': None,
                 'sigma_pb': None, 'global_acceptance': None} for energy in (13, 14)]
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp)/'a', Path(temp)/'b'
            export({'families': rows}, a)
            export({'families': [dict(reversed(list(r.items()))) for r in rows]}, b)
            self.assertEqual({p.name: p.read_bytes() for p in a.iterdir()},
                             {p.name: p.read_bytes() for p in b.iterdir()})
            self.assertIn('null', (a/'production_map_13TeV_families.csv').read_text())

    def test_complete_committed_rates_bind_every_family_and_preserve_baseline(self):
        report = load(BASE/'production_map_13_14.json')
        self.assertEqual(report['production_13TeV_gate'], 'PRODUCTION_MAP_13TEV_COMPLETE')
        self.assertEqual(report['production_14TeV_gate'], 'PRODUCTION_14TEV_PILOT_COMPLETE')
        self.assertEqual(len(report['rates']), 19)
        self.assertEqual(len(report['families']), 76)
        self.assertEqual(len(report['matrix_checks']['rows']), 320)
        original = load(BASE/'candidate_followup.json')['production_evidence']
        rates = {(r['id'], r['energy_TeV']): r for r in report['rates']}
        for r in original['rates']:
            reused = copy.deepcopy(rates[r['id'], 13]); reused.pop('origin')
            self.assertEqual(reused, r)
        for energy, count in ((13, 64), (14, 12)):
            rows = [f for f in report['families'] if f['energy_TeV'] == energy]
            self.assertEqual(len(rows), count)
            ranked = sorted(rows, key=lambda f: f['rank_at_energy'])
            self.assertEqual([r['rank_at_energy'] for r in ranked], list(range(1, count+1)))
            self.assertEqual([r['sigma_times_BR_pb'] for r in ranked],
                             sorted((r['sigma_times_BR_pb'] for r in ranked), reverse=True))
            for f in rows:
                self.assertIsNone(f['global_acceptance'])
                self.assertEqual(f['physical_bsgamma'], 'UNKNOWN')
                self.assertAlmostEqual(f['sigma_times_BR_pb'], f['sigma_pb']*f['BR_H2_H1Z'])
                self.assertAlmostEqual(f['integration_error_on_sigma_times_BR_pb'],
                                       f['integration_error_pb']*f['BR_H2_H1Z'])
                self.assertAlmostEqual(sum(f['H1_decay_BR_separate'].values()), 1.)
                self.assertEqual(f['receipt_sha256'], rates[f['id'], energy]['receipt_sha256'])
                binding = {k: f[k] for k in ('scalar_sha256', 'module2_input_sha256', 'yukawa_sha256',
                                            'mapped_card_sha256', 'receipt_sha256', 'energy_TeV')}
                self.assertEqual(digest(binding), f['binding_sha256'])
        self.assertEqual(len(report['unresolved_subTeV_opportunities']), 6)
        for r in report['unresolved_subTeV_opportunities']:
            self.assertEqual(r['gates']['vacuum']['assessment'], 'UNKNOWN')
        for name, want in load(BASE/'production_map_hashes.json').items():
            self.assertEqual(file_sha(BASE/name), want)
        with tempfile.TemporaryDirectory() as temp:
            export(report, Path(temp))
            for p in Path(temp).iterdir():
                self.assertEqual(p.read_bytes(), (BASE/p.name).read_bytes())
        for name, want in report['source_sha256'].items():
            self.assertEqual(file_sha(BASE.parents[1]/name), want)
        plots = BASE/'production_map_plots'
        manifest = load(plots/'plot_hashes.json')
        self.assertEqual(manifest['input_sha256'], file_sha(BASE/'production_map_13_14.json'))
        for name, want in manifest['artifacts'].items():
            self.assertEqual(file_sha(plots/name), want)


@unittest.skipUnless(os.environ.get('D14C_DATASET'), 'Set D14C_DATASET for retained native validation')
class NativeMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load(os.environ['D14C_DATASET'])['rows']

    def test_all_new_native_results_and_receipt_falsifiers(self):
        from module14.conditional_scan import production_map_validate as validation
        for energy, ids in ((13, REMAINING_IDS), (14, BENCHMARK_IDS)):
            for point in ids:
                result = validate_one(point, energy, [r for r in self.rows if r['id'] == point])
                self.assertEqual(result['status'], 'D14D_NATIVE_RUN_PASS')
        real_load = validation.load
        for change in ('energy', 'input', 'output', 'compiled'):
            def altered(path):
                data = real_load(path)
                if Path(path).name == 'receipt.json':
                    if change == 'energy':
                        data['energy_TeV'] = 13
                    else:
                        field = {'input': 'input_sha256', 'output': 'output_sha256',
                                 'compiled': 'compiled_source_snapshot_sha256'}[change]
                        data[field][next(iter(data[field]))] = '0'*64
                return data
            with patch.object(validation, 'load', side_effect=altered):
                with self.assertRaises(ValueError):
                    validate_one(15591, 14, [r for r in self.rows if r['id'] == 15591])
        read_text = Path.read_text

        def duplicate_process(path, *args, **kwargs):
            text = read_text(path, *args, **kwargs)
            if path == WORK/'receipt_15591_14TeV/proc_card_mg5.dat':
                text += '\nadd process g d3 > u3 hm3 QCD=1 QED=1\n'
            return text

        with patch.object(Path, 'read_text', duplicate_process):
            with self.assertRaisesRegex(ValueError, 'Charge/beam/order'):
                validate_one(15591, 14, [r for r in self.rows if r['id'] == 15591])


if __name__ == '__main__':
    unittest.main()
