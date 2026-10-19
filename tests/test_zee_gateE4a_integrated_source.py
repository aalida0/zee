"""Integrated E4A physics/source validation."""
import unittest

class TestE4A(unittest.TestCase):
    def test_import(self):
        from zee_gateE4a_integrated_precision_matching_calibration import STATUS
        self.assertIn('BLOCKED', STATUS)
