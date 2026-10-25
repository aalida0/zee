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

    def test_dirty_pinned_checkout_fails_closed(self):
        with patch.object(gate,"checked_run",side_effect=[
                subprocess.CompletedProcess([],0,stdout=gate.PIN+"\n"),
                subprocess.CompletedProcess([],1,stdout="changed fixture")]):
            with self.assertRaisesRegex(ValueError,"local changes"):
                gate.verify_checkout(ROOT)

    def test_manifest_lha_uses_official_runner_absolute_path(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            lha=root/"input.flha";lha.write_text("fixture")
            cmd=gate.official_command(Path("/build/hyperiso-ui"),root,
                "hyperiso-ui wilson summary --lha input.flha --qmatch 81 --order NNLO")
            self.assertEqual(cmd[cmd.index("--lha")+1],str(lha))
            self.assertEqual(cmd[cmd.index("--qmatch")+1],"81")

    def test_unattributed_binary_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            binary=root/"build"/"hyperiso-ui"
            binary.parent.mkdir();binary.write_bytes(b"not an upstream build")
            with self.assertRaisesRegex(ValueError,"requires a CMake build"):
                gate.verify_build(root,binary)
            (binary.parent/"CMakeCache.txt").write_text(
                "CMAKE_HOME_DIRECTORY:INTERNAL=/different/checkout\n")
            with self.assertRaisesRegex(ValueError,"different source"):
                gate.verify_build(root,binary)

if __name__=="__main__":unittest.main()
