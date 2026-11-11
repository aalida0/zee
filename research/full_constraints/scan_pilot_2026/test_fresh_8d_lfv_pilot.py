import unittest
import math
import numpy as np
from module14.scan import digest
from research.full_constraints.scan_pilot_2026 import fresh_8d_lfv_pilot as s


class Fresh8DZeePilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scalar, cls.seed, cls.spec, cls.inp = s.fresh_family()

    def test_fixed_scalar_and_fresh_family_identity(self):
        self.assertEqual(self.scalar["id"], 2264)
        self.assertEqual(self.scalar["gates"]["vacuum"]["assessment"], "PASS")
        self.assertEqual(self.scalar["bsg_nominal_classification"], "APPROX_COMPATIBLE")
        self.assertEqual(
            self.seed, digest(["d14-neutrino-v1", s.SEED, 2264, "IO", 1])
        )
        self.assertNotEqual(s.SEED, 20261104)

    def test_all_eight_directions_change_only_homogeneous_coefficients(self):
        x = np.zeros(8)
        base = s.input_at(self.inp, x)
        for i in range(8):
            y = x.copy()
            y[i] = 0.0125
            test = s.input_at(self.inp, y)
            self.assertEqual(base["target_eV"], test["target_eV"])
            self.assertEqual(base["null_cone"], test["null_cone"])
            self.assertEqual(base["scalar"], test["scalar"])
            self.assertEqual(base["lepton_masses_GeV"], test["lepton_masses_GeV"])
            self.assertNotEqual(base["homogeneous_coefficients"], test["homogeneous_coefficients"])

    def test_finite_neutrino_closure_and_partial_only(self):
        x = s.starting_vector(self.inp, 0)
        result = s.evaluate(self.inp, x)
        self.assertLess(result["neutrino_relative_closure"], 2e-9)
        self.assertTrue(math.isfinite(result["partial_BR"]))
        self.assertEqual(result["physical_LFV"], "UNKNOWN")
        self.assertIsNone(result["global_acceptance"])
        self.assertEqual(result["input_sha256"], digest(result["input"]))

    def test_outside_declared_box_fails_closed(self):
        with self.assertRaises(ValueError):
            s.input_at(self.inp, np.ones(8))
        with self.assertRaises(ValueError):
            s.input_at(self.inp, np.array([float("nan")] + [0] * 7))


if __name__ == "__main__":
    unittest.main()
