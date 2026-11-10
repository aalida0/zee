"""Synthetic source recovery tests: hash lock, missing observable, no overwrite."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from research.full_constraints.lfv_lo_closure_2026.export_native_mu3e_observable import run


class RecoverTests(unittest.TestCase):
    def fixture(self, folder):
        root = Path(folder)
        base = root/'EWSB'/'SPheno'
        (base/'Observables').mkdir(parents=True)
        source = base/'Observables'/'FlavorKit_LFV_ZeeTypeII.f90'
        source.write_text('! original source\n')
        lock = root/'lock.json'
        lock.write_text(json.dumps({'artifacts': [
            {'id': 'generated', 'path_hint': str(source),
             'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}]}))
        return base, source, lock

    def test_recovery_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            base, _, lock = self.fixture(folder)
            (base/'LowEnergy_ZeeTypeII.f90').write_text(
                'Subroutine BR1LeptonTo3Leptons(a,b)\nEnd Subroutine\n')
            output = Path(folder)/'out.zip'
            out = run(lock, output)
            self.assertEqual(len(out['files']), 1)
            with zipfile.ZipFile(output) as archive:
                self.assertIn('00_LowEnergy_ZeeTypeII.f90', archive.namelist())
            with self.assertRaises(FileExistsError):
                run(lock, output)

    def test_changed_generated_source_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            base, source, lock = self.fixture(folder)
            (base/'LowEnergy_ZeeTypeII.f90').write_text('BR1LeptonTo3Leptons')
            source.write_text('modified!')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                run(lock, Path(folder)/'out.zip')

    def test_absent_mu3e_observable_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            _, _, lock = self.fixture(folder)
            with self.assertRaisesRegex(FileNotFoundError, 'No Calculate_Lto3Lp'):
                run(lock, Path(folder)/'out.zip')

    def test_modern_sarah_flavorkit_observable(self):
        with tempfile.TemporaryDirectory() as folder:
            base, _, lock = self.fixture(folder)
            (base/'FlavorKit_Observables_ZeeTypeII.f90').write_text(
                'Subroutine Calculate_Lto3Lp(a,b)\nEnd Subroutine\n')
            output = Path(folder)/'modern.zip'
            result = run(lock, output)
            self.assertEqual(result['status'], 'MODEL_SPECIFIC_OBSERVABLE_NOT_VALIDATED')
            with zipfile.ZipFile(output) as archive:
                self.assertIn('00_FlavorKit_Observables_ZeeTypeII.f90',
                              archive.namelist())

    def test_generic_sarah_process_fallback_is_not_physics_validated(self):
        with tempfile.TemporaryDirectory() as folder:
            base, _, lock = self.fixture(folder)
            sarah_root = Path(folder)/'SARAH'
            p = sarah_root/'FlavorKit'/'LFV'/'Processes'
            p.mkdir(parents=True)
            (p/'Lto3Lp.f90').write_text('! Process-body only\n')
            output = Path(folder)/'generic.zip'
            result = run(lock, output, sarah_root)
            self.assertEqual(result['status'], 'GENERIC_TEMPLATE_ONLY')
            self.assertEqual(result['files'][0]['scope'], 'GENERIC_TEMPLATE_ONLY')

    def test_observables_nested_discovery(self):
        with tempfile.TemporaryDirectory() as folder:
            base, _, lock = self.fixture(folder)
            p = base/'Observables'/'FlavorKit_Observables_ZeeTypeII.f90'
            p.write_text('Subroutine Calculate_Lto3Lp()\nEnd Subroutine\n')
            output = Path(folder)/'nested.zip'
            result = run(lock, output)
            self.assertEqual(len(result['files']), 1)


if __name__ == '__main__':
    unittest.main()
