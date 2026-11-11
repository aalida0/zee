"""Fail-closed regression tests for h125 effective-width native Zee LFV injection."""
import math
import unittest
from research.full_constraints.pheno_paper_2026.h125_higgssignals_probe import add_native_zee_h125_lfv


class FakeParticle:
    def __init__(self, baseline=4.1e-3, defective=False):
        self.baseline=baseline
        self.widths={}
        self.defective=defective
    def totalWidth(self):
        return self.baseline + math.fsum(self.widths.values())*(2 if self.defective else 1)
    def setDecayWidth(self, name, value):
        if name in self.widths:
            raise AssertionError("Duplicate LFV final state")
        self.widths[name]=value


def fixture():
    return {"known_partial_widths_GeV":{
        "ll_e_mu":1.0e-11,"ll_e_tau":2.0e-10,"ll_mu_tau":3.0e-9}}


class HiggsSignalsLFVWidthTests(unittest.TestCase):
    def test_three_zee_flavor_offdiagonal_modes_added_exactly_once(self):
        h=FakeParticle()
        result=add_native_zee_h125_lfv(h,fixture())
        self.assertEqual(set(h.widths),{"emu","etau","mutau"})
        self.assertAlmostEqual(result["reference_before_LFV_width_GeV"],.0041)
        self.assertAlmostEqual(result["effective_after_LFV_width_GeV"],
                               .0041+3.21e-9,places=14)
        self.assertFalse(result["width_is_full_physical_Zee"])

    def test_invalid_or_missing_source_mode_fails_closed(self):
        for value in (-1.,float("nan"),float("inf")):
            x=fixture()
            x["known_partial_widths_GeV"]["ll_mu_tau"]=value
            with self.assertRaises(ValueError):
                add_native_zee_h125_lfv(FakeParticle(),x)
        x=fixture()
        del x["known_partial_widths_GeV"]["ll_e_mu"]
        with self.assertRaises(KeyError):
            add_native_zee_h125_lfv(FakeParticle(),x)

    def test_reference_width_not_zero_and_never_replaced_by_known_sum(self):
        with self.assertRaises(ValueError):
            add_native_zee_h125_lfv(FakeParticle(0.0),fixture())

    def test_duplicate_counting_diagnostic_catches_bad_adapter(self):
        with self.assertRaises(ArithmeticError):
            add_native_zee_h125_lfv(FakeParticle(defective=True),fixture())


if __name__=="__main__":
    unittest.main()
