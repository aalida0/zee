import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from module14.scan import cached_scalar_gates, digest
from module14.collect import collect
from test_module14_collect import CollectionTests


class CacheTests(unittest.TestCase):
    def test_hit_corruption_and_source_change(self):
        with tempfile.TemporaryDirectory() as d:
            row = {'scalar_sha256': digest({'x': 1})}
            gates = {'reconstruction': {'assessment': 'PASS'}}
            with patch('module14.scan.scalar_gates', return_value=gates) as call:
                self.assertEqual(cached_scalar_gates(row, d, 'version1'), gates)
                self.assertEqual(cached_scalar_gates(row, d, 'version1'), gates)
                self.assertEqual(call.call_count, 1)
                self.assertEqual(cached_scalar_gates(row, d, 'version2'), gates)
                self.assertEqual(call.call_count, 2)
            for f in Path(d).glob('*.json'):
                entry = json.loads(f.read_text())
                if entry['key']['source_version'] == 'version1':
                    entry['gates']['reconstruction']['assessment'] = 'FAIL'
                    f.write_text(json.dumps(entry))
            with self.assertRaises(ValueError):
                cached_scalar_gates(row, d, 'version1')


class ProvenanceTests(CollectionTests):
    def test_source_mismatch(self):
        part = self.worker(self.shards[0], 'source')
        with self.assertRaises(ValueError):
            collect(self.manifest, self.config, [part], source_commit='wrong')
        self.assertEqual(collect(self.manifest, self.config, [part], source_commit='LOCAL_UNSPECIFIED')['missing_points'], 2)

if __name__ == '__main__': unittest.main()
