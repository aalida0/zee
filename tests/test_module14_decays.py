import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch

from module14.decays import DecayCalculation
from module2.interface import canonical_hash


class DecayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads(Path('validation/module12/d12_benchmarks.json').read_text())['groups'][0]['witnesses']['central']
        cls.family = dict(cls.reference['yukawas'], input_sha256=canonical_hash(cls.reference['module2_input']))
        cls.scalar = cls.reference['module2_input']['scalar']['record']

    def assert_structural_numerical_close(self,observed,expected):
        """Preserve all keys/statuses, tolerate only sub-1e-11 numerical drift.

        Original D12 fixture was generated under a different Linux/BLAS
        build; a bitwise Python float comparison is not portable.
        """
        if isinstance(expected,dict):
            self.assertIsInstance(observed,dict)
            self.assertEqual(set(observed),set(expected))
            for k in expected:
                with self.subTest(key=k):
                    self.assert_structural_numerical_close(observed[k],expected[k])
        elif isinstance(expected,list):
            self.assertIsInstance(observed,list)
            self.assertEqual(len(observed),len(expected))
            for a,b in zip(observed,expected):
                self.assert_structural_numerical_close(a,b)
        elif type(expected) is float and type(observed) in (int,float):
            self.assertTrue(math.isclose(observed,expected,rel_tol=2e-11,abs_tol=1e-30),
                            f"numerical drift {observed!r} vs {expected!r}")
        else:
            self.assertEqual(observed,expected)

    def test_d12_reference_and_scalar_work_reused(self):
        from module14 import decays
        with patch('module14.decays.nonleptonic', wraps=decays.nonleptonic) as calc:
            d = DecayCalculation(self.scalar, self.family)
            a = d.evaluate(self.family)
            b = d.evaluate(self.family)
            self.assertEqual(calc.call_count, 2)
        for k in ('H1', 'H2'):
            self.assert_structural_numerical_close(a['mothers'][k]['total'],self.reference['decays'][k]['total'])
        self.assert_structural_numerical_close(a['cascade_product'],self.reference['cascade_product'])
        self.assertEqual(a, b)
        self.assertEqual(a['scalar_sha256'], canonical_hash(self.scalar))

    def test_incomplete_does_not_become_zero(self):
        d = DecayCalculation(self.scalar, self.family)
        with patch('module14.decays.complete_total', return_value={'status': 'BR_NOT_EVALUATED', 'missing_widths': ['x']}):
            r = d.evaluate(self.family)
        self.assertEqual(r['status'], 'NOT_EVALUATED')
        self.assertNotIn('cascade_product', r)

if __name__ == '__main__': unittest.main()
