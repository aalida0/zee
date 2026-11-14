"""Mock only SPheno process I/O, never assert physical one-loop LFV acceptance."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from .run_repaired64_native_source import run_native_isolated

class SPhenoNativeRunTests(unittest.TestCase):
    def test_explicit_output_and_isolated_work_directory(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);exe=d/'exe';exe.write_text('stub');inp=d/'input.in';inp.write_text('stub')
            results=d/'results';results.mkdir()
            def fake_run(cmd,*,cwd,capture_output,text,timeout,check):
                self.assertEqual(cmd[1],"input.in")
                self.assertEqual(cmd[2],"output.spc")
                self.assertEqual((Path(cwd)/"input.in").read_bytes(),inp.read_bytes())
                self.assertEqual(Path(cwd),results/'input')
                Path(cmd[2]).write_text('BLOCK MASS\n 25 125\n')
                return subprocess.CompletedProcess(cmd,0,'ok\n','')
            with patch('research.full_constraints.lfv_literature_closure_2026.run_repaired64_native_source.subprocess.run',side_effect=fake_run):
                output,log,info=run_native_isolated(exe,inp,results)
            self.assertEqual(info['output_mode'],'explicit')
            self.assertEqual(info['original_input_sha256'],info['short_input_copy_sha256'])
            self.assertIn('EXIT_STATUS 0',log.read_text())
            self.assertEqual(output.read_text(),'BLOCK MASS\n 25 125\n')

    def test_isolated_default_output_not_misidentified_as_missing(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);exe=d/'exe';exe.write_text('stub');inp=d/'input.in';inp.write_text('stub')
            results=d/'results';results.mkdir()
            def fake_run(cmd,*,cwd,**kw):
                (Path(cwd)/'SPheno.spc.ZeeTypeII').write_text('BLOCK MASS\n 25 125\n')
                return subprocess.CompletedProcess(cmd,0,'ok','')
            with patch('research.full_constraints.lfv_literature_closure_2026.run_repaired64_native_source.subprocess.run',side_effect=fake_run):
                output,log,info=run_native_isolated(exe,inp,results)
            self.assertEqual(info['output_mode'],'default')
            self.assertEqual(output.name,'SPheno.spc.ZeeTypeII')

    def test_zero_exit_without_spectrum_is_not_success(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);exe=d/'exe';exe.write_text('stub');inp=d/'input.in';inp.write_text('stub')
            results=d/'results';results.mkdir()
            def fake_run(cmd,*,cwd,**kw):
                (Path(cwd)/'Messages.out').write_text('Error: failed input handling 57')
                return subprocess.CompletedProcess(cmd,0,'fatal spectrum error','')
            with patch('research.full_constraints.lfv_literature_closure_2026.run_repaired64_native_source.subprocess.run',side_effect=fake_run):
                with self.assertRaisesRegex(RuntimeError,'failed input handling 57'):
                    run_native_isolated(exe,inp,results)
            self.assertTrue((results/'input'/'spheno.stdout.stderr.log').is_file())
            self.assertTrue((results/'input'/'Messages.out').is_file())

    def test_duplicate_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);exe=d/'exe';exe.write_text('stub');inp=d/'input.in';inp.write_text('stub')
            results=d/'results';results.mkdir()
            def fake_run(cmd,*,cwd,**kw):
                (Path(cwd)/cmd[2]).write_text('one')
                (Path(cwd)/'SPheno.spc.ZeeTypeII').write_text('two')
                return subprocess.CompletedProcess(cmd,0,'','')
            with patch('research.full_constraints.lfv_literature_closure_2026.run_repaired64_native_source.subprocess.run',side_effect=fake_run):
                with self.assertRaisesRegex(RuntimeError,'Ambiguous'):
                    run_native_isolated(exe,inp,results)

if __name__=='__main__': unittest.main()
