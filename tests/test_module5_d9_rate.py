"""Live executable falsifiers; passing tests document a BLOCKED physics gate."""
import json
import math
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def execute(command):
    result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
    values = dict((k, float(v)) for k, v in (line.split() for line in result.stdout.splitlines()))
    if not all(math.isfinite(v) for v in values.values()):
        raise AssertionError('Backend produced nonfinite output')
    return values


class PhysicalFalsifiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads((ROOT/'validation/module5/d9_bsgamma_rate.json').read_text())
        cls.rows = [(row, execute(row['command'])) for row in cls.evidence['rows']]
        cls.baseline = execute([str(ROOT/'validation/module5/local/d9/rate_probe')])

    def test_SM_full_rate_reproduces_unmodified_SM_program(self):
        # Upstream executable prints only four significant figures.
        self.assertLess(abs(self.baseline['SM_upstream_default_scale']-
                            self.evidence['official_SM_rounded']), 5e-8)
        self.assertAlmostEqual(self.baseline['SM_full'], 3.3822930662078421e-4, delta=5e-13)

    def test_same_input_LO_mass_and_signed_Yukawa_matching(self):
        for row, out in self.rows:
            for i in (7, 8):
                self.assertAlmostEqual(out[f'native_LO_C{i}']-out[f'SM_LO_C{i}'],
                                       row['independent_BMU_ordinary'][f'C{i}_LO'], delta=5e-11)

    def test_uncapped_NLO_basis_and_nonzero_C4(self):
        for row, out in self.rows:
            coeff = row['independent_BMU_ordinary']
            self.assertNotEqual(coeff['C4_NLO_raw'], 0.)
            self.assertAlmostEqual(out['native_NLO_C4']-out['SM_NLO_C4'], coeff['C4_NLO_raw'], delta=5e-11)
            for i, factor in ((7, 4/9), (8, 1/6)):
                self.assertAlmostEqual(out[f'uncapped_C{i}_NLO']+factor*coeff['C4_NLO_raw'],
                                       coeff[f'C{i}_NLO_raw'], delta=5e-11)

    def test_native_NLO_oracle_is_falsified_by_erased_dipoles(self):
        for row, out in self.rows:
            for i in (7, 8):
                self.assertEqual(out[f'native_NLO_C{i}']-out[f'SM_NLO_C{i}'], 0.)
                self.assertGreater(abs(out[f'uncapped_C{i}_NLO']), 1e-5)
            self.assertGreater(abs(out['injected_NLOmatching_native_metadata']-
                                   out['native_NLOmatching_diagnostic']), 5e-13)

    def test_low_scale_arrays_do_not_determine_full_rate(self):
        # Probe holds supplied arrays fixed and changes only native model metadata.
        out = self.rows[1][1]
        self.assertGreater(abs(out['injected_NLOmatching_native_metadata']-
                               out['injected_NLOmatching_SM_metadata']), 1e-7)

    def test_C4_is_carried_into_rate_and_cannot_be_omitted(self):
        out = self.rows[1][1]
        self.assertGreater(abs(out['injected_NLOmatching_SM_metadata']-
                               out['omit_C4_diagnostic']), 1e-10)

    def test_native_decoupling_and_opposite_ld_response(self):
        normal = [(row, out) for row, out in self.rows if row['tanbeta']==5.3 and not row['opposite_ld']]
        rates = [out['native_full'] for _, out in normal]
        self.assertTrue(all(a>b for a,b in zip(rates,rates[1:])))
        self.assertLess(abs(rates[-1]-self.baseline['SM_full']), 2e-8)
        flipped = next(out for row,out in self.rows if row['tanbeta']==5.3 and row['opposite_ld'])
        self.assertLess(flipped['native_full'], self.baseline['SM_full'])
        self.assertGreater(rates[1], self.baseline['SM_full'])

    def test_actual_executable_repeat_precision(self):
        for row, out in self.rows:
            self.assertEqual(out, row['output'])
        self.assertEqual(self.evidence['repeat_max_difference'], 0.)


if __name__ == '__main__':
    unittest.main()
