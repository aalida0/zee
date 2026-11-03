import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from module14 import scan
from module14.collect import collect


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = json.loads(Path('module14/pilot_config.json').read_text())
        self.config.update(count=4, shard_size=2)
        scan.generate(self.config, self.root / 'scan')
        self.manifest = self.root / 'scan/manifest.jsonl'
        self.shards = [self.root / 'scan/shard_000000.jsonl', self.root / 'scan/shard_000001.jsonl']

    def worker(self, shard, name, resume=False):
        out, receipt = self.root / (name + '.jsonl'), self.root / (name + '.receipt')
        with patch('module14.scan.reconstruct', return_value=({}, {}, {'assessment': 'PASS'})), \
             patch('module14.scan.check_bfb', return_value={'assessment': 'FAIL'}), \
             patch('module14.scan.unitarity', return_value={'assessment': 'PASS'}), \
             patch('module14.scan.ewpo', return_value={'assessment': 'PASS'}):
            scan.run(shard, out, receipt, self.config, resume=resume)
        return (shard, out, receipt)

    def test_shard_invariance_and_resume(self):
        full = self.worker(self.manifest, 'full')
        parts = [self.worker(p, 'part' + str(i)) for i, p in enumerate(self.shards)]
        self.assertEqual(full[1].read_bytes(), b''.join(x[1].read_bytes() for x in parts))
        a = collect(self.manifest, self.config, [full])
        b = collect(self.manifest, self.config, parts)
        self.assertEqual(a['cutflow'], b['cutflow'])
        self.assertEqual(a['status'], 'COMPLETE')
        self.assertEqual(a['cutflow']['neutrino']['NO']['NOT_EVALUATED'], 8)
        with self.assertRaises(FileExistsError):
            self.worker(self.manifest, 'full')
        self.worker(self.manifest, 'full', resume=True)
        partial = collect(self.manifest, self.config, parts[:1])
        self.assertEqual(partial['missing_points'], 2)
        self.assertEqual(partial['status'], 'INCOMPLETE')

    def test_duplicate_corruption_and_wrong_shard(self):
        part = self.worker(self.shards[0], 'part')
        with self.assertRaises(ValueError):
            collect(self.manifest, self.config, [part, part])
        with self.assertRaises(ValueError):
            collect(self.manifest, self.config, [(self.shards[1], part[1], part[2])])
        with part[1].open('a') as f:
            f.write('{}\n')
        with self.assertRaises(ValueError):
            collect(self.manifest, self.config, [part])
        with self.assertRaises(FileExistsError):
            self.worker(self.shards[0], 'part', resume=True)

    def test_rehashed_tampering_and_missing_result(self):
        shard, output, receipt = self.worker(self.shards[0], 'tampered')
        original = output.read_text().splitlines()
        rec = json.loads(receipt.read_text())
        row = json.loads(original[0])
        row['scalar_sha256'] = '0' * 64
        output.write_text(scan.encode(row) + '\n' + original[1] + '\n')
        rec['output_sha256'] = scan.file_sha(output)
        receipt.write_text(scan.encode(rec))
        with self.assertRaises(ValueError):
            collect(self.manifest, self.config, [(shard, output, receipt)])
        output.write_text(original[0] + '\n')
        rec['output_sha256'] = scan.file_sha(output)
        receipt.write_text(scan.encode(rec))
        with self.assertRaises(ValueError):
            collect(self.manifest, self.config, [(shard, output, receipt)])

    def test_missing_receipt_and_duplicate_manifest(self):
        part = self.worker(self.shards[0], 'part')
        part[2].unlink()
        with self.assertRaises(FileExistsError):
            self.worker(self.shards[0], 'part', resume=True)
        with self.manifest.open('a') as f:
            f.write(self.shards[0].read_text().splitlines()[0] + '\n')
        with self.assertRaises(ValueError):
            collect(self.manifest, self.config, [])

if __name__ == '__main__':
    unittest.main()
