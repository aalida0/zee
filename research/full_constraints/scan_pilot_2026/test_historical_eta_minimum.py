import unittest
from research.full_constraints.scan_pilot_2026 import historical_eta_minimum as h
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

class HistoricalEtaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=next(x for x in source_points() if x["id"]==2264)
        cls.f=next(x for x in cls.p["families"] if (x["ordering"],x["family"])==("IO",1))
    def test_original_signed_source_convention_and_historical_BR(self):
        v=h.amplitudes(self.p,self.f,0.0001)
        self.assertAlmostEqual(v["partial_mu_e_gamma_BR"]/1.640521548094087e-13,1,places=8)
        self.assertLess(v["neutrino_relative_closure"],2e-9)
        self.assertEqual(v["physical_LFV"],"UNKNOWN")
        self.assertEqual(v["vacuum_sufficient_certificate"],"PASS")
        self.assertIsNone(v["global_acceptance"])
    def test_source_replay_and_d4_when_partial_sub_limit(self):
        r=h.minimize_ray(self.p,self.f)
        self.assertTrue(r["best"]["partial_sub_limit"],
                        "Actual source-evaluated minimum did NOT cross bound")
        self.assertTrue(0<r["best"]["D4_BR_H2_H1Z"]<1)
        self.assertIsNone(r["best"]["global_acceptance"])
        self.assertFalse(r["best"]["same_point_13TeV_hard_process_rate_recomputed"])
    def test_disallow_outside_interval(self):
        with self.assertRaises(ValueError):
            h.amplitudes(self.p,self.f,.005)

if __name__=="__main__":
    unittest.main()
