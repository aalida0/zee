"""Deterministic, disk-backed export checks using immutable saved records."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from module14.conditional_scan.workflow import join, load
from module14.disk_rows import DiskRows, streaming_digest
from module14.final_export import export
from module14.fixtures.replay import materialize
from module14.scan import digest


class StreamingTests(unittest.TestCase):
    def test_frozen_join_and_export_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);config,manifest,parts=materialize(root/'inputs', {50,91})
            args=(manifest,config,parts,load('module14/conditional_scan/matching_card.json'),'LOCAL_UNSPECIFIED','LOCAL_UNSPECIFIED')
            legacy=join(*args)
            streamed=join(*args,streaming=True)
            try:
                self.assertEqual(list(streamed['rows']),legacy['rows'])
                self.assertEqual(streaming_digest(streamed),digest(legacy))
                export(legacy,root/'legacy');export(streamed,root/'stream')
                self.assertEqual({p.name:p.read_bytes() for p in (root/'legacy').iterdir()},
                                 {p.name:p.read_bytes() for p in (root/'stream').iterdir()})
                reversed_data=join(manifest,config,list(reversed(parts)),*args[3:],streaming=True)
                try:
                    self.assertEqual(streaming_digest(reversed_data),streaming_digest(streamed))
                finally: reversed_data['rows'].close()
                bad=copy.deepcopy(legacy);bad['rows'].append(bad['rows'][0])
                with self.assertRaisesRegex(ValueError,'Duplicate'):export(bad,root/'duplicate')
                self.assertFalse((root/'duplicate').exists())
                bad=copy.deepcopy(legacy);bad['rows'][0]['scalar_sha256']='0'*64
                with self.assertRaises(ValueError):export(bad,root/'wrong-source')
                self.assertFalse((root/'wrong-source').exists())
                bad=copy.deepcopy(legacy);bad['collection']['missing_points']=1
                with self.assertRaises(ValueError):export(bad,root/'missing')
                self.assertFalse((root/'missing').exists())
                with patch('module14.final_export.os.rename',side_effect=KeyboardInterrupt):
                    with self.assertRaises(KeyboardInterrupt):export(legacy,root/'retry')
                self.assertFalse((root/'retry').exists())
                self.assertFalse((root/'retry.export-lock').exists())
                export(legacy,root/'retry')
                with self.assertRaises(FileExistsError):export(legacy,root/'retry')
            finally:streamed['rows'].close()

    def test_disk_rows_json_and_index(self):
        rows=DiskRows()
        try:
            values=[{'id':2,'neutrino':None},{'id':1,'neutrino':None}]
            for r in values:rows.append(r)
            self.assertEqual(rows[-1],values[-1]);self.assertEqual(list(rows.sorted()),list(reversed(values)))
            self.assertEqual(streaming_digest({'rows':rows}),digest({'rows':values}))
            with self.assertRaises(IndexError):_ = rows[2]
        finally:rows.close()

    def test_optional_original_225_export_bytes(self):
        path=Path('/tmp/zee-d14c-dataset.json')
        if not path.exists():self.skipTest('Optional original 225-point saved dataset absent')
        from module14.scan import file_sha
        self.assertEqual(file_sha(path),'2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9')
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(export(load(path),Path(tmp)/'export'),load('module14/fixtures/saved_225_export_audit.json'))
