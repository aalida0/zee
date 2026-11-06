import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from module14.external import bsgamma, higgstools
from unittest.mock import patch
import subprocess

PROBE = '/home/amine/zee/workspaces/zee-bsgamma-d9b/validation/module5/local/d9b/rate_probe'

class ExternalTests(unittest.TestCase):
    def test_missing_and_invalid_runtime(self):
        self.assertEqual(bsgamma({}, None)['status'], 'NOT_EVALUATED')
        self.assertEqual(higgstools({}, {}, None, None)['status'], 'NOT_EVALUATED')
        with tempfile.NamedTemporaryFile() as f:
            self.assertEqual(bsgamma({}, f.name)['status'], 'ERROR')

    @unittest.skipUnless(Path(PROBE).is_file(), 'Validated D9B probe unavailable')
    def test_d9b_reference_cache_and_corruption(self):
        r = json.loads(Path('validation/module5/d9b_superiso_repair.json').read_text())['two_state']['decoupled']
        s = {'physical': {'mH1': r['m1_GeV'], 'mH2': r['m2_GeV'], 'gamma': r['gamma_rad'], 'beta': math.atan(r['tanbeta'])}}
        with tempfile.TemporaryDirectory() as d:
            native = subprocess.CompletedProcess([], 0, stdout='injected_BR '+str(r['BR'])+'\n')
            with patch('module14.external.subprocess.run', return_value=native):
                a = bsgamma(s, PROBE, d)
            self.assertEqual(a['branching_ratio'], r['BR'])
            self.assertEqual(a, bsgamma(s, PROBE, d))
            path = next(Path(d).iterdir()); obj = json.loads(path.read_text()); obj['value']['branching_ratio'] = 0
            path.write_text(json.dumps(obj))
            with self.assertRaises(ValueError): bsgamma(s, PROBE, d)

if __name__ == '__main__': unittest.main()
