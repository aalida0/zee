"""Offline tests for the *runtime harness*, not HyperIso or Zee physics."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"zee_module5_hyperiso_runtime.py"
spec=importlib.util.spec_from_file_location("zee_hyperiso_gate",SCRIPT)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class TestPinnedGate(unittest.TestCase):
    def test_pins(self):
        self.assertEqual(gate.VERSION,"1.0.3")
        self.assertEqual(gate.PIN,"09d26ac6e71d1528922097a896d15693589f636b")
        self.assertEqual(gate.CASES,("R1","R3","R6"))

    def test_nonbinary_fails_without_writing_output(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            upstream=root/"upstream";upstream.mkdir()
            dest=root/"out"/"report.json"
            with patch("sys.argv",["gate","--upstream",str(upstream),
                                   "--binary",str(root/"MISSING"),"--output",str(dest)]):
                with self.assertRaises((ValueError,FileNotFoundError)):
                    gate.main()
            self.assertFalse(dest.exists())

    def test_mismatched_upstream_head_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);upstream=root/"upstream";upstream.mkdir()
            binary=root/"stub";binary.write_text("#!/bin/sh\nexit 0\n");binary.chmod(0o755)
            dest=root/"out"/"report.json"
            with patch("sys.argv",["gate","--upstream",str(upstream),
                                   "--binary",str(binary),"--output",str(dest)]):
                with patch.object(gate,"checked_run",return_value=subprocess.CompletedProcess(
                    ["git","rev-parse","HEAD"],0,stdout="wrong\n",stderr="")):
                    with self.assertRaises(ValueError):
                        gate.main()
            self.assertFalse(dest.exists())

if __name__=="__main__":unittest.main()
