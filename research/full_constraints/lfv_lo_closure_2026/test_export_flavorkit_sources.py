"""Synthetic file tests for the read-only, hash-checked Zee FlavorKit exporter."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from research.full_constraints.lfv_lo_closure_2026.export_flavorkit_sources import (
    collect, export
)


class ExportTest(unittest.TestCase):
    def make_fixtures(self, root):
        entries = []
        overrides = {}
        for name in ('generated', 'couplings', 'loops'):
            path = root / (name + '.f90')
            path.write_text(f'! {name}\nsubroutine CalculatePengV4L(a)\nend subroutine\n')
            entries.append({'id':name, 'path_hint':str(path),
                            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            overrides[name] = path
        lock = root/'lock.json'
        lock.write_text(json.dumps({'artifacts':entries}))
        return lock, overrides

    def test_hash_contract_zip_contents_and_immutability(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            lock, overrides = self.make_fixtures(root)
            target=root/'pack.zip'
            out=export(lock,target,overrides)
            with zipfile.ZipFile(target) as a:
                self.assertEqual(sorted(a.namelist()),
                    ['SOURCE_EXPORT_RECEIPT.json','couplings.f90','generated.f90','loops.f90'])
                self.assertEqual(a.read('generated.f90'),overrides['generated'].read_bytes())
            self.assertIn('CalculatePengV4L',
                out['entries']['generated']['lexical_index']['subroutines_lfv_named'])
            with self.assertRaises(FileExistsError):
                export(lock,target,overrides)
            self.assertEqual(hashlib.sha256(overrides['generated'].read_bytes()).hexdigest(),
                             json.loads(lock.read_text())['artifacts'][0]['sha256'])

    def test_modified_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            lock, overrides=self.make_fixtures(root)
            overrides['couplings'].write_text('changed')
            with self.assertRaisesRegex(RuntimeError,'SHA256 MISMATCH'):
                collect(lock, overrides)
            self.assertFalse((root/'pack.zip').exists())

    def test_missing_source_is_not_silent(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            lock,overrides=self.make_fixtures(root)
            overrides['generated'].unlink()
            with self.assertRaisesRegex(RuntimeError,'source not found'):
                collect(lock,overrides)


if __name__=='__main__':
    unittest.main()
