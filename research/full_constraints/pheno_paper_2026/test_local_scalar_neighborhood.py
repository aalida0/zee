import copy
import math
import unittest

from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.pheno_paper_2026 import local_scalar_neighborhood as s


class LocalNeighborhoodSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards={p["id"]:p for p in source_points()}

    def test_exact_pinned_scalar_center_not_modified(self):
        for id in s.CENTERS:
            card=self.cards[id]["input_card"]
            cloned,policy=s.perturbed_point(card,id,0)
            self.assertEqual(card,cloned)
            self.assertEqual(policy["variation_type"],"exact_original_scalar_source")
            self.assertEqual(self.cards[id]["gates"]["vacuum"]["assessment"],"PASS")

    def test_bounds_and_determinism_hold_with_frozen_original_source(self):
        for id in s.CENTERS:
            original=self.cards[id]["input_card"]
            a,ap=s.perturbed_point(original,id,3)
            b,bp=s.perturbed_point(original,id,3)
            self.assertEqual(a,b)
            self.assertEqual(ap,bp)
            self.assertEqual(original["physical"]["mH2"],self.cards[id]["input_card"]["physical"]["mH2"])
            self.assertLess(abs(a["physical"]["gamma"]-original["physical"]["gamma"]),s.DELTA_GAMMA+1e-12)
            oldtan=math.tan(original["physical"]["beta"])
            self.assertLess(abs(math.tan(a["physical"]["beta"])/oldtan-1.),s.REL_TANBETA+1e-12)
            self.assertGreater(a["physical"]["mH2"]-a["physical"]["mH1"],
                               a["electroweak"]["mZ"]+20.)

    def test_neighborhood_is_not_an_allowed_model_scan(self):
        self.assertEqual(s.CENTERS,(15673,15591,14074))
        self.assertEqual(s.VARIATIONS_PER_CENTER,16)
        self.assertEqual(s.ONE_SIDED_Z,1.6448536269514722)
        self.assertNotIn("global_acceptance",s.perturbed_point(self.cards[15673]["input_card"],15673,1)[1])


if __name__=="__main__":
    unittest.main()
