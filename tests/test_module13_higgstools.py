"""Physics/status falsifiers for the bounded HiggsTools run (no generators)."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from module13 import higgstools as ht


REPORT = json.loads((ht.OUT/'d13_higgstools.json').read_text())


class HiggsToolsChecks(unittest.TestCase):
    def test_exact_frozen_benchmarks_and_unrenormalized_brs(self):
        for name, result in REPORT['benchmarks'].items():
            record, witness = ht.inputs(name)
            assert record['input_sha256'] == result['scalar_sha256']
            for h in result['charged_inputs']:
                decay = witness['decays'][h['particle']]['total']
                assert h['branching_fractions'] == decay['branching_fractions']
                assert h['total_width_GeV'] == decay['total_width_GeV']
                self.assertAlmostEqual(sum(h['branching_fractions'].values()), 1.)


    def test_missing_charged_production_is_unknown(self):
        tmp_path = Path(tempfile.mkdtemp())
        self.addCleanup(__import__('shutil').rmtree, tmp_path)
        (tmp_path/'higgstools_production_inputs.json').write_text('{"records": []}')
        with patch.object(ht, 'OUT', tmp_path):
            assert ht.production('D7', 2, ht.inputs('D7')[1]) is None


    def test_mismatched_scalar_rate_is_rejected(self):
        tmp_path = Path(tempfile.mkdtemp())
        self.addCleanup(__import__('shutil').rmtree, tmp_path)
        data = json.loads((ht.OUT/'higgstools_production_inputs.json').read_text())
        data = copy.deepcopy(data)
        row = next(r for r in data['records'] if r['name'] == 'D7' and r['state'] == 2)
        row['benchmark']['physical']['mH2'] += 1
        (tmp_path/'higgstools_production_inputs.json').write_text(json.dumps(data))
        with patch.object(ht, 'OUT', tmp_path), self.assertRaises(AssertionError):
            ht.production('D7', 2, ht.inputs('D7')[1])


    def test_expected_selection_and_central_rate_exclusion(self):
        for name, result in REPORT['benchmarks'].items():
            hb = result['charged_HB']
            for particle, selected in hb['selected'].items():
                alternatives = [a for a in hb['applied'] if particle in a['particles']]
                assert selected['expected_ratio'] == max(a['expected_ratio'] for a in alternatives)
                assert selected['id'] == 210210076
            assert hb['status'] == ('EXCLUDED' if name == 'D7' else 'NOT_EXCLUDED')
        self.assertAlmostEqual(REPORT['benchmarks']['D7']['charged_HB']['selected']['H2']['observed_ratio'], 1.0723832487416896)


    def test_tiny_tau_rates_retained_and_missing_not_passed(self):
        for result in REPORT['benchmarks'].values():
            rows = result['charged_HB']['applied']
            tau = [a for a in rows if a['id'] in (1903045601, 1807079152)]
            assert len(tau) == 4
            assert all(0 < a['expected_ratio'] < 1e-4 for a in tau)
            absent = [a for a in result['charged_analysis_coverage'] if a['status'] == 'UNEVALUATED']
            assert absent and all(not a['results'] for a in absent)
            assert all(a['status'] == 'NOT_APPLICABLE' for a in result['charged_analysis_coverage'] if 'vbfHpm' in a['analysis'])


    def test_signals_sum_and_no_full_acceptance(self):
        assert REPORT['global_zee_acceptance'] is None
        for result in REPORT['benchmarks'].values():
            hs = result['HiggsSignals']
            self.assertAlmostEqual(sum(m['chi2'] for m in hs['measurements']), hs['chi2'])
            assert hs['observable_count'] == 159
            self.assertAlmostEqual(hs['delta_chi2'], hs['chi2']-hs['chi2_SM'])
            assert result['heavy_neutral']['status'] == 'UNEVALUATED'
            assert hs['status'].startswith('UNEVALUATED_FULL_MODEL')
            assert result['global_zee_acceptance'] is None


if __name__ == '__main__':
    unittest.main()
