import copy
import json
from pathlib import Path
import tempfile
import unittest

from module1.scalar_constraints import validate_input
from module14.scan import generate


class HeavyScanTests(unittest.TestCase):
    def test_heavy_valid_coverage_and_reproducibility(self):
        config = json.loads(Path('module14/heavy_scan_config.json').read_text())
        config.update(count=200, shard_size=25)
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/'a', Path(tmp)/'b'
            generate(config, a)
            generate(config, b)
            self.assertEqual((a/'manifest.jsonl').read_bytes(), (b/'manifest.jsonl').read_bytes())
            rows = [json.loads(s) for s in (a/'manifest.jsonl').read_text().splitlines()]
            self.assertEqual(b''.join(p.read_bytes() for p in sorted(a.glob('shard_*.jsonl'))), (a/'manifest.jsonl').read_bytes())
            self.assertEqual(len({r['scalar_sha256'] for r in rows}), 200)
            counts = {}
            for r in rows:
                p = r['scalar']
                validate_input(p)
                x = p['physical']
                self.assertEqual(x['mh1'], 125)
                self.assertGreater(x['mH2'], x['mH1'] + p['electroweak']['mZ'] + 20)
                self.assertGreaterEqual(x['mH2'], 700)
                self.assertLessEqual(x['mH2'], 2000)
                counts[r['arm']] = counts.get(r['arm'], 0) + 1
                if r['arm'] != 'broad_control':
                    lo, hi = map(int, r['arm'].split('_')[1:])
                    self.assertTrue(lo <= x['mH2'] <= hi)
            self.assertEqual(sorted(counts.values()), [20, 60, 60, 60])

    def test_legacy_regression(self):
        config = json.loads(Path('module14/pilot_config.json').read_text())
        config.update(count=1, shard_size=1)
        with tempfile.TemporaryDirectory() as tmp:
            generate(config, Path(tmp)/'out')
            row = json.loads((Path(tmp)/'out/manifest.jsonl').read_text())
            self.assertEqual(row['scalar_sha256'], 'bb6880bc2217e5f6492c6354bfaca68886f85befaaa11ca31649b78d05e38918')

    def test_invalid_range_rejected(self):
        config = json.loads(Path('module14/heavy_scan_config.json').read_text())
        config = copy.deepcopy(config)
        config['arms'][0]['ranges']['tanbeta'] = [0, 15]
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            generate(config, Path(tmp)/'out')


if __name__ == '__main__':
    unittest.main()
