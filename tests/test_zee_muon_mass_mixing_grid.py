"""Paper 2 broad mass–mixing gauge-only grid regression checks."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_muon_mass_mixing_grid import (
    STATUS,ALPHA_YW,SW2_YW,numbers,point,generate,
)
from zee_muon_asymmetric_pair_pilot import sigma_both_charges_fb


class TestMuonMassMixingGrid(unittest.TestCase):
    def test_scheme_matched_to_successful_mg5_benchmark(self):
        sigma=point(207.25762719087444,686.4739736697521,
                    1.1845311184933986,1500.,.5)[
                        "sigma_Z_both_charges_fb"]
        self.assertAlmostEqual(sigma,.5862261608252013,delta=1e-10)
        self.assertAlmostEqual(SW2_YW,.23369913342182436,delta=1e-12)
        self.assertAlmostEqual(ALPHA_YW,1/127.9,delta=1e-14)

    def test_both_charge_conjugates_and_exact_threshold(self):
        self.assertEqual(point(400,1200,.8,1500,.5)[
                         "sigma_Z_both_charges_fb"],0.)
        q=point(400,1200,.8,3000,1)
        self.assertTrue(q["kinematically_open"])
        self.assertGreater(q["sigma_Z_both_charges_fb"],0)

    def test_zero_mix_and_maximal_mix(self):
        z=point(200,700,0.,1500.,1)
        m=point(200,700,math.pi/4,1500,1)
        k=point(200,700,1.18453,1500,1)
        self.assertEqual(z["sigma_Z_both_charges_fb"],0)
        self.assertGreater(m["sigma_Z_both_charges_fb"],
                           k["sigma_Z_both_charges_fb"])

    def test_all_mass_points_provisional_not_allowed(self):
        x=point(200,500,.8,1500,1)
        self.assertTrue(x["H1_to_tb_open"])
        self.assertTrue(x["cascade_H2_to_H1Z_open"])
        self.assertFalse(x["experimental_and_scalar_constraints_evaluated"])
        self.assertFalse(x["neutrino_t_channel_evaluated"])
        self.assertIn("NOT_ALLOWED",x["status"])

    def test_do_not_reuse_old_BRs(self):
        self.assertNotIn("BR",str(point(300,800,.8,3000,1).keys()))
        self.assertIn("GAUGE_ONLY",STATUS)

    def test_grid_range_and_luminosities(self):
        rows=generate([200,400],[500,700],[.4,.8],
                      [1500,3000],[.5,1.])
        self.assertEqual(len(rows),16)
        self.assertEqual(sum(r["sqrt_s_GeV"]==1500 for r in rows),8)
        self.assertEqual(sum(r["sqrt_s_GeV"]==3000 for r in rows),8)

    def test_invalid_mix_and_broken_energy_lists(self):
        with self.assertRaisesRegex(ValueError,"mixing"):
            generate([200],[700],[2.],[1500],[1.])
        with self.assertRaisesRegex(ValueError,"same length"):
            generate([200],[700],[.8],[1500,3000],[1.])
        with self.assertRaisesRegex(ValueError,"duplicate"):
            numbers("200,200","mass")
        with self.assertRaisesRegex(ValueError,"Bad"):
            numbers("200,not-a-number","mass")


if __name__=="__main__":
    unittest.main()
