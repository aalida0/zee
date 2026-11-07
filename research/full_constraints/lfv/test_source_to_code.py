"""Integration regressions for signed published subsets and honest coverage."""
import json
from pathlib import Path
import tempfile
import unittest

from .source_to_code import HERE, run


class PublishedSourceControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=run(HERE/'SOURCE_TO_CODE_SOURCES.json')

    def test_complex_box_and_published_real_Z(self):
        tests=self.result['tests']
        self.assertEqual(tests['generated_F_box_controls'],28)
        self.assertLess(tests['max_complex_relative_residual'],2e-12)
        self.assertLess(max(x['max_residual'] for x in tests['Z_real_integral_crosscheck']),2e-8)

    def test_scalar_vector_interference_falsifies_source_sign(self):
        x=self.result['conversion']
        au=x['flavorkit_scalar']['records'][4]
        self.assertAlmostEqual(au['source_over_reference'],1.0697235742499855,places=12)
        iso=x['flavorkit_pure_isovector_and_interference']
        self.assertLess(iso[2]['source_over_reference'],1e-12)
        self.assertGreater(iso[2]['correct_pn_assignment_rate'],2.)

    def test_missing_operators_cannot_be_physical_prediction(self):
        self.assertEqual(self.result['status'],'LFV_ONE_LOOP_BLOCKED')
        for row in self.result['records']:
            self.assertTrue(all(x is None for x in row['complete_mu3e_operator_vector'].values()))
            self.assertIsNone(row['physical_BR'])
        self.assertIsNone(self.result['exclusion'])

    def test_modified_source_lock_rejected(self):
        lock=json.loads((HERE/'SOURCE_TO_CODE_SOURCES.json').read_text())
        lock['artifacts'][0]['sha256']='0'*64
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'lock.json'; path.write_text(json.dumps(lock))
            with self.assertRaises(AssertionError):
                run(path)


if __name__=='__main__':
    unittest.main()
