import json
import unittest
from pathlib import Path
from unittest.mock import patch

from module2.interface import evaluate, canonical_hash
from module14.lfv import evaluate_family


class LFVTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads(Path('validation/module12/d12_benchmarks.json').read_text())['groups'][0]['witnesses']['central']
        inp = cls.reference['module2_input']
        out = evaluate(inp)
        cls.family = {k: out[k] for k in ('F', 'D', 'Ye', 'Ye2', 'Mnu')}
        cls.family.update(input=inp, input_sha256=canonical_hash(inp))

    def test_d12_coherent_and_tree_reference(self):
        out = evaluate_family(self.family, True)
        self.assertEqual(out['status'], 'PARTIAL')
        for name, result in out['channels'].items():
            self.assertEqual(result['partial_BR'], self.reference['radiative'][name])
            self.assertEqual(result['comparison']['status'], 'DIAGNOSTIC_ONLY')
            self.assertEqual(result['omitted_topologies']['W_gamma'], 'UNKNOWN')
        self.assertEqual(out['mu_to_3e']['tree_subset_BR'], self.reference['mu_to_3e_tree'])

    def test_optional_tree_and_input_binding(self):
        with patch('module14.lfv.tree.width', side_effect=AssertionError('unexpected tree calculation')):
            out = evaluate_family(self.family)
        self.assertEqual(out['mu_to_3e']['status'], 'NOT_EVALUATED')
        with self.assertRaises(ValueError):
            evaluate_family(dict(self.family, input_sha256='bad'))

if __name__ == '__main__': unittest.main()
