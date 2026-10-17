"""Paper2 scalar-matched UFO card mapping tests, no neutrino-fit claim."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_muon_make_scalar_card import make_card
from gate7_map_p2_to_yangwu import map_point
from gate7_make_diagnostic_param_card import replacements

class TestZeeMuonScalarCard(unittest.TestCase):
    def test_generalized_mapping_exactly_matches_historical_anchor(self):
        old=map_point(1.394,300.,700.)
        new=map_point(beta=1.394,mH1=300.,mH2=700.)
        self.assertEqual(old["map"],new["map"])

    def test_scanned_point_mapping_changes_quartics_mass_mixing(self):
        p={
            "id":"B4_0000318",
            "mH1":207.25762719087444,
            "mH2":686.4739736697521,
            "mh2":600.8714508079514,
            "ma":634.4121423462443,
            "alpha":1.4389666701508221,
            "beta":1.3955777541543262,
            "gamma":1.1845311184933986,
            "m12sq":60788.22257515175,
            "lc":4.298263955719913,
            "k1":1.563625671105378,
            "k2":0.0033232647514316567,
            "k12":-0.0008113817688472317,
        }
        opts={k:p[k] for k in (
            "alpha","gamma","m12sq","mh2","ma","lc","k1","k2","k12")}
        x=map_point(beta=p["beta"],mH1=p["mH1"],mH2=p["mH2"],**opts)
        val=replacements(beta=p["beta"],mH1=p["mH1"],
                         mH2=p["mH2"],**opts)
        self.assertEqual(x["map"]["MASS"][227],p["mH2"])
        self.assertEqual(x["map"]["MASS"][228],p["mH1"])
        self.assertEqual(x["map"]["MASS"][225],p["mh2"])
        self.assertEqual(x["map"]["MASS"][226],p["ma"])
        self.assertAlmostEqual(
            val[("ZEEINPUTS",4)],math.pi/2-p["gamma"],delta=1e-12)
        self.assertAlmostEqual(val[("ZEELAMS",7)],p["lc"],delta=1e-12)
        self.assertTrue(all(abs(v)<1e-8 for v in
                            x["closure_mass_basis_residuals"].values()))
        self.assertEqual(val[("ZEEYUKAWAF",1)],0.)
        self.assertEqual(val[("ZEEYUKAWAF",2)],0.)
        self.assertEqual(val[("ZEEYUKAWAF",3)],0.)
        self.assertNotAlmostEqual(
            val[("ZEELAMS",4)],replacements()[("ZEELAMS",4)],delta=1e-6)

    def test_unknown_scanned_keys_forbidden(self):
        with self.assertRaisesRegex(ValueError,"Unknown"):
            map_point(extra_collider_setting=10)


if __name__=="__main__":
    unittest.main()
