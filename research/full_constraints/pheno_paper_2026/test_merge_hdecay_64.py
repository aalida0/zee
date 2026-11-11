"""Regression checks for physically scoped AnyHdecay + 64-family Zee H/A joining."""
from pathlib import Path
import copy,json
import unittest
import numpy as np
from research.full_constraints.higgs.decays_bridge import read_output
from research.full_constraints.pheno_paper_2026.hdecay_16_bridge import extract
from research.full_constraints.pheno_paper_2026.heavy_HA_tree_widths import heavy_tree_channels
from research.full_constraints.pheno_paper_2026.merge_hdecay_64 import merge_one

ROOT=Path(__file__).resolve().parents[3]
REC=ROOT/"research/full_constraints/higgs/neutral_receipts"

class NativeMixedOrderNeutralMergeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=json.loads((REC/"F13_EXECUTION.json").read_text())["physical"]
        cls.ref=extract(read_output(REC/"anyhdecay-F13.stdout"),p)
        cls.native={s:heavy_tree_channels(p,np.zeros((3,3),dtype=complex),s) for s in ("H","A")}

    def test_disjoint_native_Zee_Hdecay_and_exotic_width_channels(self):
        for state in ("H","A"):
            merged=merge_one(self.native[state],self.ref[state],state)
            self.assertIsNone(merged["full_physical_total_width_GeV"])
            self.assertIsNone(merged["normalized_physical_branching_fractions"])
            self.assertEqual(merged["full_Higgs"],"UNKNOWN")
            ch=merged["channel_widths_GeV"]
            self.assertIn("gg",ch)
            self.assertIn("H1 W both charges",ch)
            self.assertIn("t tbar",ch)
            self.assertNotIn("R2HDM total width",ch)
            self.assertAlmostEqual(merged["mixed_order_known_channel_sum_GeV"],sum(ch.values()),places=10)
            self.assertAlmostEqual(ch["bb" if False else "b bbar"],
                                   self.ref[state]["transferable_partial_widths_GeV"]["bb"])

    def test_refuse_missing_QCD_channels_and_inconsistent_states(self):
        d=copy.deepcopy(self.ref["H"])
        del d["transferable_partial_widths_GeV"]["gg"]
        with self.assertRaises(ValueError):
            merge_one(self.native["H"],d,"H")
        d=copy.deepcopy(self.ref["H"])
        d["completes_Zee_total_width"]=True
        with self.assertRaises(ValueError):
            merge_one(self.native["H"],d,"H")
        d=copy.deepcopy(self.ref["H"])
        d["mass_GeV"]+=1
        with self.assertRaises(ValueError):
            merge_one(self.native["H"],d,"H")

    def test_qcd_widths_cannot_be_negative_or_physical_BRs_by_default(self):
        d=copy.deepcopy(self.ref["A"])
        d["transferable_partial_widths_GeV"]["tt"]=-1
        with self.assertRaises(ValueError):
            merge_one(self.native["A"],d,"A")

if __name__=="__main__":
    unittest.main()
