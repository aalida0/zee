"""Fixed first-octant Zee IO neutrino phase and mass observables.

These numerical constants are independent local python/numpy checks
of the same five-entry symmetry-basis charged-lepton texture.
"""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_IO_witness_neutrino_physical_observables import (
    STATUS,calculate
)

class TestFamilyZ2FirstOctantPhysicalNu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row=calculate()

    def test_dirac_phase_uses_independent_sin_and_cos(self):
        x=self.row
        self.assertAlmostEqual(x["delta_CP_degrees_mod360"],
                               217.2061973,places=5)
        self.assertAlmostEqual(x["sin_delta_CP"]**2+
                               x["cos_delta_CP"]**2,1.,places=8)
        self.assertLess(x["sin_delta_CP"],0.)
        self.assertLess(x["cos_delta_CP"],0.)

    def test_majorana_takagi_and_beta_observables(self):
        x=self.row
        self.assertLess(x["Takagi_diagonalization_max_error_eV"],1e-9)
        self.assertAlmostEqual(x["effective_beta_decay_mass_mbeta_eV"],
                               0.04951911633,places=8)
        self.assertAlmostEqual(
            x["light_exchange_0nubb_effective_mass_mbb_eV"],
            0.02154104229,places=8)
        self.assertAlmostEqual(x["sum_mnu_eV"],
                               0.1061990453,places=8)

    def test_yukawa_scales_and_fail_closed_interpretation(self):
        x=self.row
        self.assertIn("NO_LIKELIHOOD",STATUS)
        self.assertLess(x["charged_lepton_mass_closure_GeV"],1e-9)
        self.assertLess(x["max_abs_f_mass_basis"],1e-4)
        self.assertLess(x["max_abs_Y_2022_mass_basis"],1.)
        self.assertFalse(x["NuFIT_v6_1_IO_likelihood_done"])
        self.assertFalse(x["complete_LFV_done"])
        self.assertIsNone(x["full_Zee_allowed"])

if __name__=="__main__":
    unittest.main()
