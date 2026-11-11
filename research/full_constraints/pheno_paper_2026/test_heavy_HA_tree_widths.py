import math
import unittest
import numpy as np

from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.pheno_paper_2026 import heavy_HA_tree_widths as s


class HeavyZeeTreePartialWidthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards={p["id"]:p for p in source_points()}
        cls.d=np.zeros((3,3),dtype=complex)

    def test_heavy_source_15673_tree_channel_positivity_and_incomplete_total(self):
        p=self.cards[15673]["input_card"]["physical"]
        for state in ("H","A"):
            h=s.heavy_tree_channels(p,self.d,state)
            self.assertEqual(h["state"],state)
            self.assertGreater(h["known_tree_disjoint_sum_GeV"],0)
            self.assertIsNone(h["physical_total_width_GeV"])
            self.assertIsNone(h["HiggsTools_observed_exclusion"])
            self.assertEqual(h["full_Higgs"],"UNKNOWN")
            self.assertGreater(h["channels_tree_GeV"]["t tbar"],0)
            self.assertGreater(h["channels_tree_GeV"]["H1 W both charges"],0)
            self.assertGreaterEqual(h["channels_tree_GeV"]["tau tau"],0)
            self.assertLessEqual(h["tree_partial_BR_upper_bound"]["tau tau"],1)
            self.assertFalse(h["on_shell_missing"])

    def test_reproduce_independently_source_Hhh_pair_nondegenerate_count(self):
        p=self.cards[15591]["input_card"]["physical"]
        heavy=s.heavy_tree_channels(p,self.d,"H")
        self.assertGreater(heavy["channels_tree_GeV"]["H1+ H1-"],0)
        self.assertNotIn("H2+ H2- and c.c.",heavy["channels_tree_GeV"])
        self.assertEqual(len([k for k in heavy["channels_tree_GeV"] if k=="H2+ H2-"]),1)
        self.assertEqual(len([k for k in heavy["channels_tree_GeV"] if k=="H1+ H2- and c.c."]),1)
        self.assertAlmostEqual(sum(heavy["channels_tree_GeV"].values()),
                               heavy["known_tree_disjoint_sum_GeV"],places=10)
        self.assertEqual(len(heavy["channels_tree_GeV"]),6+6+2+1+2+3)

    def test_vector_width_mass_threshold_and_tau_upper_bound_definitions(self):
        self.assertEqual(s.vv_width(100,80.379,246.21965,1,False),0)
        a=s.vv_width(500,80.379,246.21965,1,False)
        b=s.vv_width(500,80.379,246.21965,0.5,False)
        self.assertGreater(a,0)
        self.assertAlmostEqual(b/a,0.25,places=12)
        with self.assertRaises(ValueError):
            s.heavy_tree_channels(self.cards[15673]["input_card"]["physical"],self.d,"h")


if __name__=="__main__":
    unittest.main()
