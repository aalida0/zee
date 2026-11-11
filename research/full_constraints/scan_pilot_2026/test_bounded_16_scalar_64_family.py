import unittest
from research.full_constraints.scan_pilot_2026.bounded_16_scalar_64_family import (
    SEEDS,ORDERINGS
)
from research.full_constraints.scan_pilot_2026.analytic_direct_lfv_textures import build
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

class SixteenScalarEnsembleSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards={p["id"]:p for p in source_points()}

    def test_only_sixteen_original_certified_no_large_scan(self):
        self.assertEqual(len(self.cards),16)
        self.assertEqual(SEEDS,(20261111,20261112))
        self.assertEqual(ORDERINGS,("NO","IO"))
        self.assertEqual(sum(p["gates"]["vacuum"]["assessment"]=="PASS"
                             for p in self.cards.values()),16)

    def test_missing_actual_production_is_none_not_zero(self):
        target=self.cards[14074]
        self.assertIsNone(target["families"][0]["production"])
        r=build(target,"NO",SEEDS[0],allowed_ids=tuple(self.cards))
        self.assertIsNone(r["original_13TeV_LO_quark_sigma_pb"])
        self.assertIsNone(r["13TeV_LO_quark_invariant_cascade_proxy_fb"])
        self.assertEqual(r["physical_LFV"],"UNKNOWN")
        self.assertIsNone(r["global_acceptance"])
        self.assertLess(r["neutrino_closure"],2e-9)

if __name__=="__main__":unittest.main()
