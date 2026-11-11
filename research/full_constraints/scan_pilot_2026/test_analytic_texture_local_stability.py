import math
import unittest
from pathlib import Path
import tempfile

from research.full_constraints.scan_pilot_2026 import analytic_texture_local_stability as s


class LocalAlgebraicFlavorStabilityTests(unittest.TestCase):
    def test_bounded_2_spectra_and_no_full_lfv(self):
        self.assertEqual(s.BENCHMARKS,((15591,"NO",20261111),(15673,"IO",20261111)))
        self.assertEqual(s.RADII,(1e-7,1e-6,1e-5,1e-4))
        with tempfile.TemporaryDirectory() as tmp:
            data=s.run(Path(tmp)/"original_output.json")
        self.assertEqual(len(data["cases"]),2)
        self.assertEqual(data["physical_LFV"],"UNKNOWN")
        self.assertIsNone(data["global_acceptance"])
        self.assertIsNone(data["allowed_8d_volume"])
        for c in data["cases"]:
            self.assertEqual(len(c["local_direction_tests"]),4)
            for v in c["local_direction_tests"]:
                self.assertEqual(v["n_trials"],40)
                self.assertGreaterEqual(v["n_perturbative"],0)
                self.assertLessEqual(v["n_retained_partial_below_limit"],40)
                self.assertTrue(v["not_volume_fraction"])


if __name__=="__main__":
    unittest.main()
