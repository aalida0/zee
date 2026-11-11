"""Independent F13 public HDECAY transfer regression and cross-scheme controls."""
from pathlib import Path
import copy
import json
import math
import unittest
import tempfile

from research.full_constraints.higgs.decays_bridge import read_output
from research.full_constraints.pheno_paper_2026.hdecay_16_bridge import (
    auxiliary_doublet_charged_mass,driver_arguments,extract,read_scoped_hdecay_reference,
)

ROOT=Path(__file__).resolve().parents[3]
RECEIPTS=ROOT/"research/full_constraints/higgs/neutral_receipts"

class PublicHdecayZeeTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference=json.loads((RECEIPTS/"F13_EXECUTION.json").read_text())
        cls.p=cls.reference["physical"]
        cls.raw=read_output(RECEIPTS/"anyhdecay-F13.stdout")

    def test_auxiliary_curvature_mass_exact_replayed_F13_source(self):
        self.assertAlmostEqual(auxiliary_doublet_charged_mass(self.p),
                               self.reference["doublet_curvature_mass_GeV"],places=10)
        args=driver_arguments(self.p)
        self.assertEqual(len(args),8)
        for x,expected in zip(args,self.reference["command"][1:]):
            self.assertAlmostEqual(x,float(expected),places=9)

    def test_actual_F13_hdecay_quark_QCD_and_gauge_spectra_transfer_only(self):
        result=extract(self.raw,self.p)
        self.assertEqual(set(result),{"H","A"})
        for state in ("H","A"):
            rec=result[state]
            self.assertFalse(rec["completes_Zee_total_width"])
            self.assertGreater(rec["transferable_partial_widths_GeV"]["tt"],0)
            self.assertGreater(rec["transferable_partial_widths_GeV"]["gg"],0)
            self.assertGreater(rec["source_R2HDM_total_width_GeV_REJECTED_ZEE"],0)
            self.assertAlmostEqual(rec["source_R2HDM_BRs_sum"],1,places=9)
            self.assertNotIn("WpHm",rec["transferable_partial_widths_GeV"])
            self.assertNotIn("tautau",rec["transferable_partial_widths_GeV"])
            self.assertNotIn("gamgam",rec["transferable_partial_widths_GeV"])
            self.assertNotIn("Zgam",rec["transferable_partial_widths_GeV"])

    def test_falsify_source_Hhh_gauge_and_br_normalization(self):
        for key,factor in (("b_Hh_HlHl",1.2),("b_A_ZHl",1.5),
                           ("SM_b_H_WW",1.1),("b_A_bb",1.15)):
            corrupted=copy.deepcopy(self.raw)
            corrupted[key]*=factor
            with self.assertRaises(ValueError,msg=key):
                extract(corrupted,self.p)

    def test_negative_reference_only_SM_gluon_diagnostic_is_not_transferred(self):
        # Original 11016 HDECAY 6.60 returns a negative SM-only gg
        # control; true H/A model gg partial widths remain positive.
        raw=self.raw.copy()
        raw["SM_b_H_gg"]=-0.0004116456134061433
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"receipt.txt"
            out.write_text("".join(f"{k} {v:.17g}\\n" for k,v in raw.items()))
            parsed,flags=read_scoped_hdecay_reference(out)
            self.assertEqual(flags,{"SM_b_H_gg":raw["SM_b_H_gg"]})
            self.assertEqual(parsed["b_Hh_gg"],self.raw["b_Hh_gg"])
            self.assertGreater(extract(parsed,self.p)["H"]["transferable_partial_widths_GeV"]["gg"],0)
            for key,value in (("b_Hh_gg",-1.e-4),("SM_b_H_WW",-1.e-4),
                              ("SM_b_H_gg",-.05)):
                tampered=raw.copy();tampered[key]=value
                out.write_text("".join(f"{k} {v:.17g}\\n" for k,v in tampered.items()))
                with self.assertRaises(ValueError):
                    read_scoped_hdecay_reference(out)

    def test_reject_corrupted_reference_widths(self):
        for value in (float("nan"),float("inf"),-1.0):
            corrupted=copy.deepcopy(self.raw)
            corrupted["w_A"]=value
            with self.assertRaises(ValueError):
                extract(corrupted,self.p)

if __name__=="__main__":
    unittest.main()
