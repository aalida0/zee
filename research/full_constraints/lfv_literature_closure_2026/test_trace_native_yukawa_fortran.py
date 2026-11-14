"""Source-only sanity tests; no claim that generated native SPheno works."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .trace_native_yukawa_fortran import inspect, contextual

class NativeSourceTraceTests(unittest.TestCase):
    def test_targets_exact_compiled_generated_fortran(self):
        with TemporaryDirectory() as d:
            p=Path(d)
            (p/"Boundaries_ZeeTypeII.f90").write_text(
                "Subroutine SetMatchingConditions(x)\n fzee = fzeeIN\n Ye2 = Ye2IN\n End Subroutine\n")
            (p/"SPhenoZeeTypeII.f90").write_text(
                "fzee = fzeeIN\n Ye2 = Ye2IN\n Call SetMatchingConditions(x)\n")
            r=inspect(p)
            self.assertIn("BOUNDARY_LOW_SCALE_F_FROM_INPUT_PRESENT True",r)
            self.assertIn("BOUNDARY_LOW_SCALE_YE2_FROM_INPUT_PRESENT True",r)
            self.assertIn("Subroutine SetMatchingConditions",r)
            self.assertIn("FULL_ZEE_LFV_UNKNOWN",r)
            self.assertFalse((p/"trace.txt").exists())
    def test_fail_closed_missing_source_dir(self):
        with TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                inspect(Path(d)/"no_source")
    def test_context_line_numbers_are_stable(self):
        self.assertEqual(contextual(["a","b","c"],2,3),"    2 b\n    3 c")

if __name__=="__main__": unittest.main()
