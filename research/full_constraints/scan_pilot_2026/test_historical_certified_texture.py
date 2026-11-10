import unittest
from research.full_constraints.scan_pilot_2026 import historical_certified_texture as s

class HistoricalCertifiedTextureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=s.source_points()
    def test_exact_historical_16_scalar_and_64_neutrino_family_ids(self):
        self.assertEqual(len(self.rows),16)
        self.assertEqual(len({x["id"] for x in self.rows}),16)
        self.assertTrue(all(x["gates"]["vacuum"]["assessment"]=="PASS" for x in self.rows))
    def test_original_F_D_leptonic_4complex_replay_on_source(self):
        original=self.rows[0]["families"][0]
        r=s.one_family(self.rows[0],original,1.0)
        self.assertEqual(r["status"],"NEUTRINO_PASS_LFV_PARTIAL")
        self.assertEqual(r["vacuum_certificate"],"PASS")
        self.assertEqual(r["physical_B"],"UNKNOWN")
        self.assertEqual(r["physical_LFV"],"UNKNOWN")
        self.assertIsNone(r["global_acceptance"])
        self.assertEqual(r["neutrino_input_sha256"],original["input_sha256"])
    def test_zero_homogeneous_neutrino_closure_replay(self):
        x=s.one_family(self.rows[0],self.rows[0]["families"][0],0.0)
        self.assertLess(x["neutrino_closure"],2e-9)
        self.assertIsNone(x["global_acceptance"])
        self.assertEqual(x["physical_LFV"],"UNKNOWN")
    def test_wrong_eta_fails(self):
        with self.assertRaises(ValueError):s.one_family(self.rows[0],self.rows[0]["families"][0],0.002)

if __name__=="__main__":
    unittest.main()
