"""Source-independent NNLO discrepancy postprocessing checks (no BR claims)."""
import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1p_diagnose_nnlo_discrepancies import diagnose,excerpts

def fake_result():
    rows=[]
    for mass in (300.,700.,1000.,2000.):
        for order,ops in ((0,("C7","C8")),
                          (1,("C4","C7","C8")),
                          (2,("C3","C4","C5","C6","C7","C8"))):
            for op in ops:
                delta=0.
                if order==2:
                    dx=-.008*300/mass
                    values={
                        "C3":dx,"C4":.02*300/mass,
                        "C5":-dx/10.,"C6":-3.*dx/16.,
                        "C7":.0005*300/mass,"C8":-.04*300/mass
                    }
                    delta=values[op]
                rows.append({
                    "mass_GeV":mass,"order":order,"operator":op,
                    "superiso_minus_hepfit":delta,
                    "relative_error":0.06 if order==2 else 0.,
                })
    return {
        "source":"HEPfit THDMMatching::setWCbsg independent of SuperIso",
        "compared_coefficients":rows,
        "failed_count":0,"NNLO_above_one_percent_relative_count":13
    }

class TestNNLOSourceAudit(unittest.TestCase):
    def test_C5_C6_are_inherited_from_C3(self):
        d=diagnose(fake_result())
        self.assertEqual(len(d["masses"]),4)
        self.assertTrue(d["C5_C6_disagreement_from_C3_alone"])
        for row in d["masses"]:
            self.assertLess(abs(row["C5_residual_after_minus_C3_over10_relation"]),1e-12)
            self.assertLess(abs(row["C6_residual_after_minus_3C3_over16_relation"]),1e-12)
        self.assertEqual(d["status"],"GATE_A1P_NNLO_SOURCE_REVIEW_REQUIRED_BLOCKED")
        self.assertIsNone(d["Zee_benchmark_excluded"])

    def test_independent_C6_mismatch_is_not_misclassified(self):
        fake=fake_result()
        next(r for r in fake["compared_coefficients"]
             if r["mass_GeV"]==300 and r["order"]==2 and
                r["operator"]=="C6")["superiso_minus_hepfit"]+=0.01
        with self.assertRaisesRegex(ValueError,"not explained solely"):
            diagnose(fake)

    def test_incomplete_comparison_is_rejected(self):
        fake=fake_result()
        fake["compared_coefficients"].pop()
        with self.assertRaisesRegex(ValueError,"44 unique"):
            diagnose(fake)

    def test_source_excerpts_preserve_original_line_numbers(self):
        text=["nothing","C3H_2 = foo","C4H_2 = bar","other"]
        sample=excerpts(text,lambda_wrapper(),1,4,1,50)
        self.assertIn("    2: C3H_2 = foo",sample["excerpts"])
        self.assertIn("    3: C4H_2 = bar",sample["excerpts"])
        self.assertFalse(sample["truncated"])

def lambda_wrapper():
    import re
    return re.compile("C[34]H_2")

if __name__=="__main__":
    unittest.main()
