"""Backward compatibility from immutable records, without proposal generation."""
import json
from pathlib import Path
import tempfile
import unittest

from module1.scalar_constraints import validate_input
from module14.scan import digest
from module14.fixtures.replay import materialize, saved


class HeavyScanTests(unittest.TestCase):
    def test_saved_legacy_input_hashes_and_identity(self):
        data = saved()
        config = json.loads(data['pilot_config.json'])
        rows = [json.loads(s) for s in data['pilot_manifest.jsonl'].splitlines()]
        self.assertEqual(len(rows), 100)
        self.assertEqual(rows[0]['scalar_sha256'], 'bb6880bc2217e5f6492c6354bfaca68886f85befaaa11ca31649b78d05e38918')
        self.assertEqual(len({r['id'] for r in rows}), 100)
        for row in rows:
            validate_input(row['scalar'])
            self.assertEqual(row['scalar_sha256'], digest(row['scalar']))
            self.assertEqual(row['config_sha256'], digest(config))

    def test_saved_repartition_reproduces_original_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, parts = materialize(Path(tmp), shard_size=25)
            self.assertEqual(manifest.read_bytes(), saved()['pilot_manifest.jsonl'])
            self.assertEqual(b''.join(t[1].read_bytes() for t in parts), saved()['pilot_output.jsonl'])

    def test_historical_heavy_config_is_unchanged(self):
        config = json.loads(Path('module14/heavy_scan_config.json').read_text())
        self.assertEqual(config['count'], 20000)
        self.assertEqual([a['weight'] for a in config['arms']], [3,3,3,1])
        historical = json.loads(Path('module14/conditional_scan/production_map_13_14.json').read_text())
        self.assertIsNone(historical['global_acceptance'])


if __name__ == '__main__': unittest.main()
