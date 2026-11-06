import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from module14.scan import file_sha
from module14.conditional_scan import candidate_export as export
from module14.conditional_scan.candidate_vacuum import diagnose
from module14.conditional_scan.workflow import load, production
from module14.conditional_scan.targeted_validation import validate_one, validate_run_card
from module14.conditional_scan.targeted_production import WORK

BASE = export.BASE
DATASET = os.environ.get('D14C_DATASET')


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = load(BASE/'remote_conditional_summary.json')

    def test_derived_intersections_and_original_ids(self):
        groups, counts = export.shortlist(self.summary)
        self.assertEqual(counts['points'], 225)
        self.assertEqual(counts['vacuum'], {'PASS': 33, 'UNKNOWN': 192})
        self.assertEqual(counts['nominal_bsgamma'], {'APPROX_COMPATIBLE': 77, 'APPROX_DISFAVORED': 148})
        self.assertEqual(len(groups[export.CERTIFIED]), 16)
        self.assertEqual(groups[export.LIGHT], [3582, 3821, 6850, 11920, 13512, 17671])
        self.assertEqual(counts['certified_subtev'], 0)
        self.assertTrue(set(export.PRODUCTION_IDS).issubset(groups[export.CERTIFIED]))

    def test_shortlist_rejects_changed_identity_or_acceptance(self):
        for change in ('scalar', 'id', 'acceptance'):
            summary = copy.deepcopy(self.summary)
            point = summary['points']['15591']
            if change == 'scalar':
                point['input_card']['physical']['mH2'] += 1
            elif change == 'id':
                point['id'] = 2264
            else:
                point['globally_allowed'] = True
            with self.assertRaises(ValueError):
                export.shortlist(summary)

    def test_finite_vacuum_scope(self):
        with self.assertRaises(ValueError):
            diagnose({'id': 3821})
        for starts in (0, 193, True):
            with self.assertRaises(ValueError):
                diagnose({'id': 3582}, starts=starts)

    def test_separate_proposal_and_frozen_evidence_sources(self):
        original = load(BASE/'followup_config.json')
        proposed = load(BASE/'next20k_proposal.json')
        self.assertEqual(proposed['count'], 20000)
        self.assertEqual(proposed['seed'], 20261107)
        self.assertNotEqual(proposed['seed'], original['seed'])
        self.assertEqual([arm['weight'] for arm in proposed['arms']], [3, 5, 2])
        self.assertEqual(proposed['arms'][1]['ranges']['mH2'], [1000, 1350])
        for old, new in zip(original['arms'], proposed['arms']):
            for key in old['ranges'].keys()-{'mH2'}:
                self.assertEqual(old['ranges'][key], new['ranges'][key])
        evidence = load(BASE/'candidate_followup.json')
        for name, want in evidence['source_sha256'].items():
            self.assertEqual(file_sha(export.ROOT/name), want)
        production_evidence = evidence['production_evidence']
        self.assertEqual(file_sha(export.ROOT/'module14/conditional_scan/targeted_validation.py'),
                         production_evidence['validation_source_sha256'])
        for name, want in production_evidence['mapping']['source_sha256'].items():
            self.assertEqual(file_sha(export.ROOT/name), want)

    def test_published_diagnostics_never_promote_absence(self):
        report = load(BASE/'candidate_followup.json')
        for candidate in report['tables'][export.LIGHT]:
            row = candidate['separate_vacuum_diagnostic']
            self.assertEqual(row['assessment'], 'UNKNOWN')
            self.assertEqual(candidate['gates']['vacuum']['assessment'], 'UNKNOWN')
            if candidate['id'] in export.VACUUM_IDS:
                self.assertEqual(len(row['bounded_search']['runs']), 199)
                self.assertFalse(row['certificate_attempt']['certified'])
                self.assertFalse(row['bounded_search']['global_stability_proven'])
                self.assertIsNone(row['verified_deeper_stationary_witness'])
            else:
                self.assertEqual(row['search_status'], 'NOT_EVALUATED')

    def test_same_energy_family_binding_and_null_missing_production(self):
        report = load(BASE/'candidate_followup.json')
        bound = []
        for candidates in report['tables'].values():
            for candidate in candidates:
                self.assertIsNone(candidate['global_acceptance'])
                self.assertEqual(candidate['physical_bsgamma'], 'UNKNOWN')
                for family in candidate['families']:
                    self.assertIsNone(family['global_acceptance'])
                    self.assertEqual(family['lfv_coverage']['complete_lfv'], False)
                    if family['production']:
                        bound.append(family)
                        rate = family['production']
                        self.assertEqual(rate['energy_TeV'], 13.)
                        self.assertAlmostEqual(family['yield_proxy_pb'], rate['sigma_pb']*family['cascade_BR'], places=16)
                        self.assertAlmostEqual(family['integration_error_on_proxy_pb'], rate['integration_error_pb']*family['cascade_BR'], places=17)
                    else:
                        self.assertIsNone(family['yield_proxy_pb'])
                        self.assertIsNone(family['rank'])
        self.assertEqual(len(bound), 12)
        self.assertEqual(sorted(f['rank'] for f in bound), list(range(1, 13)))
        self.assertEqual(len({f['module2_input_sha256'] for f in bound}), 12)
        self.assertEqual(len({f['production']['scalar_level_receipt_sha256'] for f in bound}), 3)

    def test_run_card_energy_pdf_and_scale_falsifiers(self):
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
        validate_run_card(raw, 1035.7)
        for before, after in [('6500 = ebeam1', '6800 = ebeam1'),
                              ('1035.7 = scale', '700 = scale'), ('263000 = lhaid', '1 = lhaid')]:
            with self.assertRaises(ValueError):
                validate_run_card(raw.replace(before, after), 1035.7)


@unittest.skipUnless(DATASET, 'Set D14C_DATASET to the immutable full AF dataset')
class FullDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load(DATASET)
        cls.row = next(r for r in cls.data['rows'] if r['id'] == 15591)
        cls.compact = next(f for f in load(BASE/'remote_conditional_summary.json')['points']['15591']['families']
                           if (f['ordering'], f['family']) ==
                              (cls.row['neutrino']['ordering'], cls.row['neutrino']['family']))

    def test_actual_family_and_decay_falsifiers(self):
        export.verify_family(self.row, self.compact)
        for what in ('input', 'yukawa', 'width', 'source'):
            row = copy.deepcopy(self.row)
            if what == 'input':
                row['neutrino']['input_sha256'] = '0'*64
            elif what == 'yukawa':
                row['widths']['yukawa_sha256']['F'] = '0'*64
            elif what == 'width':
                row['widths']['mothers']['H2']['channels'].pop()
            else:
                key = next(iter(row['neutrino']['module2_provenance']['code_sha256']))
                row['neutrino']['module2_provenance']['code_sha256'][key] = '0'*64
            with self.assertRaises(ValueError):
                export.verify_family(row, self.compact)

    def test_unknown_certificate_no_search_witness_stays_unknown(self):
        candidate = next(c for c in load(BASE/'candidate_followup.json')['tables'][export.LIGHT] if c['id'] == 3582)
        no_witness = {'lowest_credible_minimum': None, 'runs': [], 'global_stability_proven': False}
        with patch('module14.conditional_scan.candidate_vacuum.constrained_search', return_value=no_witness):
            result = diagnose(candidate, starts=16)
        self.assertEqual(result['assessment'], 'UNKNOWN')
        self.assertFalse(result['certificate_attempt']['certified'])

    @unittest.skipUnless((WORK/'validated_production.json').exists(), 'Native artifacts not retained on this host')
    def test_actual_native_runs_and_wrong_receipt_scale(self):
        from module14.conditional_scan import targeted_validation as validation
        for point_id in export.PRODUCTION_IDS:
            rows = [r for r in self.data['rows'] if r['id'] == point_id]
            self.assertEqual(validate_one(point_id, rows)['status'], 'D14C_NATIVE_RUN_PASS')
        real_load = validation.load

        def changed(path):
            data = real_load(path)
            if Path(path).name == 'receipt.json':
                data['muR_GeV'] = 700.
            return data

        with patch.object(validation, 'load', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'Receipt scale mismatch'):
                validate_one(15591, [r for r in self.data['rows'] if r['id'] == 15591])

    @unittest.skipUnless((WORK/'production').exists(), 'Native family contracts not retained on this host')
    def test_actual_contract_rejects_wrong_family(self):
        row = self.row; n = row['neutrino']
        path = WORK/'production'/(n['input_sha256']+'.json')
        production(path, row['input_card'], n)
        changed = copy.deepcopy(n); changed['input_sha256'] = '0'*64
        with self.assertRaises(ValueError):
            production(path, row['input_card'], changed)
        contract = load(path)
        with tempfile.TemporaryDirectory() as temporary:
            bad = Path(temporary)/'contract.json'
            contract['artifacts_sha256'] = {'missing-real-result.dat': '0'*64}
            bad.write_text(json.dumps(contract))
            with self.assertRaises((ValueError, FileNotFoundError)):
                production(bad, row['input_card'], n)


if __name__ == '__main__':
    unittest.main()
