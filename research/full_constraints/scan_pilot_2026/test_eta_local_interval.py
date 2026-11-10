import unittest
from research.full_constraints.scan_pilot_2026 import eta_local_interval as r
from research.full_constraints.scan_pilot_2026.vacuum_followup import strict_inputs

class HomogeneousRayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cards={v["id"]:v for v in strict_inputs()}
    def test_same_original_partial_eta0_and_eta1(self):
        s=self.cards[284]
        a=r.partial_BR(s,"IO",4,0.0)
        b=r.partial_BR(s,"IO",4,1.)
        self.assertAlmostEqual(a/5.543766908080203e-15,1.,places=10)
        self.assertAlmostEqual(b/2.3282355932488707e-7,1.,places=10)
        self.assertLess(a,r.MEG_II)
        self.assertGreater(b,r.MEG_II)
    def test_local_bidirectional_brackets(self):
        x=r.interval(self.cards[284],"IO",4)
        self.assertEqual(x["crossings"]["positive"]["status"],"LOCALLY_BRACKETED")
        self.assertEqual(x["crossings"]["negative"]["status"],"LOCALLY_BRACKETED")
        self.assertGreater(x["crossings"]["positive"]["eta_threshold"],0)
        self.assertLess(x["crossings"]["negative"]["eta_threshold"],0)
        self.assertEqual(x["physical_LFV"],"UNKNOWN")
        self.assertIsNone(x["global_acceptance"])
    def test_bad_eta(self):
        with self.assertRaises(ValueError):
            r.partial_BR(self.cards[284],"NO",0,float("nan"))
        with self.assertRaises(ValueError):
            r.partial_BR(self.cards[284],"NO",0,1.1)

if __name__=="__main__":
    unittest.main()
