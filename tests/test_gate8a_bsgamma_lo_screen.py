"""Gate 8A B->Xs gamma LO matching: Type-II one-state limits and Zee mixing."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate8a_bsgamma_lo_screen import (
    screen, typeii_charged_lo, loop_functions
)


class TwoChargedHiggsFlavorScreen(unittest.TestCase):
    def test_reference_pilot_LO_values(self):
        r=screen()
        self.assertAlmostEqual(r["mixing_weight_light_cos2gamma"],0.21471339018904734)
        self.assertAlmostEqual(r["mixing_unitarity_sum"],1.)
        self.assertAlmostEqual(
            r["combined_LO_charged_scalar"]["DeltaC7"],-0.06296082441633363,
            places=12)
        self.assertAlmostEqual(
            r["combined_LO_charged_scalar"]["DeltaC8"],-0.06612190677250937,
            places=12)
        self.assertAlmostEqual(
            r["combined_over_reference_LO"]["DeltaC7"],1.0636565105604519,
            places=11)
        self.assertAlmostEqual(
            r["combined_over_reference_LO"]["DeltaC8"],1.0317118504197411,
            places=11)

    def test_gamma_zero_is_typeii_light_only(self):
        r=screen(gamma=0)
        light=r["individual_TypeII_LO_matching"]["light"]
        for c in ("C7","C8"):
            self.assertAlmostEqual(
                r["combined_LO_charged_scalar"]["Delta"+c],
                light[c],places=12)

    def test_gamma_halfpi_is_typeii_heavy_only(self):
        r=screen(gamma=math.pi/2)
        heavy=r["individual_TypeII_LO_matching"]["heavy"]
        for c in ("C7","C8"):
            self.assertAlmostEqual(
                r["combined_LO_charged_scalar"]["Delta"+c],
                heavy[c],places=12)

    def test_degenerate_charged_masses_are_gamma_independent(self):
        a=screen(mH1=600,mH2=600.001,gamma=0.1)
        b=screen(mH1=600,mH2=600.001,gamma=1.4)
        self.assertLess(
            abs(a["combined_LO_charged_scalar"]["DeltaC7"]-
                b["combined_LO_charged_scalar"]["DeltaC7"]),1e-6)

    def test_invalid_threshold_and_inputs(self):
        with self.assertRaises(ValueError):
            loop_functions(1)
        with self.assertRaises(ValueError):
            typeii_charged_lo(0,5,172)
        with self.assertRaises(ValueError):
            screen(mH1=700,mH2=300)


if __name__=="__main__":
    unittest.main()
