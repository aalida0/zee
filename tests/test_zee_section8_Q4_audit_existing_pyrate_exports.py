"""Q4 AST-only inspection of existing PyR@TE export (NO generation/physics claims)."""
import ast
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_audit_existing_pyrate_exports import (
    EXPECTED_BETA,static_inspect,STATUS
)

class TestQ4ExistingExportAudit(unittest.TestCase):
    def mock_export(self,root,skip=(),invalid=False):
        src=root/'GeneralZee_CANDIDATE_NOT_VALIDATED'/'PythonOutput'
        src.mkdir(parents=True)
        expressions=[]
        for names in EXPECTED_BETA.values():
            expressions.extend(
                'def beta_'+name+'(nLoop):\n    return nLoop\n\n'
                for name in names if name not in skip
            )
        (src/'RGEs.py').write_text(''.join(expressions)+
                                   ('def beta_bad(:\n' if invalid else ''))
        (src/'run.py').write_text('print("DO_NOT_RUN")\n')
        (src/'GeneralZee_CANDIDATE_NOT_VALIDATED.py').write_text(
            'print("DO_NOT_IMPORT")\n')
        return src
    def test_full_export_inventory_is_static_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            self.mock_export(root)
            data=static_inspect(root)
            self.assertTrue(data['static_export_complete'])
            self.assertEqual(data['exported_beta_function_count'],26)
            self.assertIn('beta_f',data['exported_beta_function_names'])
            self.assertFalse(data['general_complex_Zee_RGEs_physics_validated'])
            self.assertFalse(data['independent_RGBeta_crosscheck_validated'])
            self.assertIsNone(data['physical_Zee_allowed'])
    def test_missing_f_does_not_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            self.mock_export(root,skip=('f',))
            data=static_inspect(root)
            self.assertFalse(data['static_export_complete'])
            self.assertEqual(data['missing_expected_beta_functions']['yukawa'],['f'])
    def test_missing_complex_scalar_terms_does_not_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            self.mock_export(root,skip=('l6','l7','l10'))
            data=static_inspect(root)
            self.assertFalse(data['static_export_complete'])
            self.assertEqual(data['missing_expected_beta_functions']['quartic'],['l6','l7','l10'])
    def test_syntax_invalid_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            self.mock_export(root,invalid=True)
            with self.assertRaisesRegex(ValueError,'Invalid generated Python syntax'):
                static_inspect(root)
    def test_output_must_exist(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                static_inspect(Path(folder)/'not_created')
    def test_no_duplicate_beta_function_names(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            src=self.mock_export(root)
            with (src/'RGEs.py').open('a') as f:
                f.write('\ndef beta_f(nLoop): return 0\n')
            with self.assertRaisesRegex(ValueError,'Duplicate top-level RGE'):
                static_inspect(root)
    def test_requires_exported_run_and_model_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            src=self.mock_export(root)
            (src/'run.py').unlink()
            with self.assertRaisesRegex(ValueError,'run.py export missing'):
                static_inspect(root)
    def test_never_executes_generated_module(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            src=self.mock_export(root)
            (src/'RGEs.py').write_text(
                (src/'RGEs.py').read_text()+'\nraise RuntimeError("EXECUTED")\n')
            # AST parsing must not run the file.
            self.assertTrue(static_inspect(root)['static_export_complete'])

if __name__=='__main__':unittest.main()
