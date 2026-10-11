"""Gate7D electroweak scheme/threshold analytic closure tests."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate7_ew_scheme_audit import derive_ew,read_ew_inputs,audit
from gate6_width_inventory import inventory

INPUT="""Block SMINPUTS
    1 1.279000e+02 # alpha^-1
    2 1.166370e-05 # GF
Block MASS
 23 91.1876 # Z
 25 125.0
 225 580.7
 226 633.7
 227 700.0
 228 300.0
DECAY 227 0.01
"""

OUT="""DECAY 227 1.2367270e+01 # heavy
  8.84108e-02 2 24 225  # W hheavy
  7.609846e-01 2 23 228 # Z light
DECAY 228 9.520432e-02 # light
  9.553033e-01 2 6 -5
"""


class SchemeTests(unittest.TestCase):
    def test_onshell_derived_values(self):
        z=derive_ew(127.9,1.16637e-5,91.1876)
        self.assertAlmostEqual(z["MW_GeV"],79.82435974619784,places=10)
        self.assertAlmostEqual(z["sin2thetaW"],0.23369913342182436,places=10)
        self.assertAlmostEqual(z["gW"],0.648397167195027,places=9)

    def test_card_inputs(self):
        z=read_ew_inputs(INPUT)
        self.assertEqual(z["alpha_inv"],127.9)
        self.assertEqual(z["Gf_GeVminus2"],1.16637e-5)

    def test_real_width_discrepancy_explained_by_input_scheme(self):
        z=audit(INPUT,OUT)
        self.assertAlmostEqual(z["expected_EW_scheme_ratio"],1.0209243630375555,places=10)
        self.assertTrue(z["EW_scheme_explains_width_at_0p1pct"])
        self.assertLess(abs(z["relative_residual_after_EW_match"]),1e-3)

    def test_fails_on_wrong_masses(self):
        with self.assertRaisesRegex(ValueError,r"MASS\[225\]"):
            audit(INPUT.replace("225 580.7","225 580.8"),OUT)

    def test_missing_sm_inputs_rejected(self):
        with self.assertRaisesRegex(ValueError,"SMINPUTS"):
            read_ew_inputs("Block SMINPUTS\n1 127.9\n")


if __name__=="__main__":
    unittest.main()
