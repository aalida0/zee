"""Tests: original-author 48-row matching discrepancy decomposition."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1q_audit_numeric_author_residuals import close_numeric_comparison
from gateA1p_audit_effective_operator_basis import Y,Z
from gateA1q_inspect_original_mathematica import PINNED_KIT_SHA256

def fixture():
    rows=[]
    for mass in (300,700,1000,2000):
        for order in (0,1):
            for op in (7,8):
                rows.append({
                    "mass_GeV":mass,"author_order":order,"operator":f"C{op}",
                    "original_author":1.,"SuperIso_in_author_basis":1.,
                    "HEPfit_in_author_basis":1.,
                    "SuperIso_minus_author":0.,"HEPfit_minus_author":0.,
                })
        four={}
        for op in (3,4,5,6):
            author=op/100.
            si=author+op/1000.
            four[op]={"author":author,"si":si,"hf":author}
            rows.append({
                "mass_GeV":mass,"author_order":2,"operator":f"C{op}",
                "original_author":author,"SuperIso_in_author_basis":si,
                "HEPfit_in_author_basis":author,
                "SuperIso_minus_author":si-author,"HEPfit_minus_author":0.,
            })
        for op,w in ((7,Y),(8,Z)):
            raw_author=10.+op
            si_raw=raw_author+.0001
            hf_raw=raw_author+.01
            rows.append({
                "mass_GeV":mass,"author_order":3,"operator":f"C{op}",
                "original_author":raw_author,
                "SuperIso_in_author_basis":si_raw,
                "HEPfit_in_author_basis":hf_raw,
                "SuperIso_minus_author":si_raw-raw_author,
                "HEPfit_minus_author":hf_raw-raw_author,
            })
            author_eff=raw_author+sum(w[i]*four[i]["author"] for i in w)
            si_eff=si_raw+sum(w[i]*four[i]["si"] for i in w)
            hf_eff=hf_raw+sum(w[i]*four[i]["hf"] for i in w)
            rows.append({
                "mass_GeV":mass,"author_order":2,"operator":f"C{op}",
                "original_author":author_eff,
                "SuperIso_in_author_basis":si_eff,
                "HEPfit_in_author_basis":hf_eff,
                "SuperIso_minus_author":si_eff-author_eff,
                "HEPfit_minus_author":hf_eff-author_eff,
            })
    assert len(rows)==48
    return {
        "original_author_source_sha256":PINNED_KIT_SHA256,
        "comparison_rows":rows,
    }

class TestOriginalAuthorResidualClosure(unittest.TestCase):
    def test_full_exact_decomposition(self):
        x=close_numeric_comparison(fixture())
        self.assertIn("HEPFIT_CLOSES",x["status"])
        self.assertEqual(len(x["rows"]),12)
        self.assertTrue(x["HEPfit_matches_authors_C3_C6_exact_numerical"])
        self.assertTrue(x["SuperIso_C3_C6_has_author_discrepancy"])
        self.assertTrue(x["SuperIso_raw_C7_C8_closer_to_authors_all_8"])
        self.assertTrue(x["all_eight_effective_residuals_decomposed"])
        self.assertFalse(x["full_NNLO_matching_validated"])
        self.assertFalse(x["BtoXs_gamma_BR_validated"])
        self.assertIsNone(x["Zee_benchmark_allowed"])
        self.assertIsNone(x["Zee_benchmark_excluded"])

    def test_corrupted_effective_basis_closure_blocks(self):
        obj=fixture()
        item=next(r for r in obj["comparison_rows"] if
                  r["mass_GeV"]==700 and r["author_order"]==2
                  and r["operator"]=="C8")
        item["SuperIso_minus_author"]+=.01
        with self.assertRaisesRegex(ValueError,"closure FAILED"):
            close_numeric_comparison(obj)

    def test_missing_author_row_blocks(self):
        obj=fixture()
        obj["comparison_rows"].pop()
        with self.assertRaisesRegex(ValueError,"48"):
            close_numeric_comparison(obj)

    def test_unpinned_mathematica_source_blocks(self):
        obj=fixture()
        obj["original_author_source_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"checksum"):
            close_numeric_comparison(obj)

    def test_altered_hepfit_fourquark_no_longer_exacts(self):
        obj=fixture()
        four=next(r for r in obj["comparison_rows"] if
                  r["mass_GeV"]==1000 and r["author_order"]==2
                  and r["operator"]=="C3")
        four["HEPfit_minus_author"]=0.0001
        for op,weights in ((7,Y),(8,Z)):
            eff=next(r for r in obj["comparison_rows"] if
                  r["mass_GeV"]==1000 and r["author_order"]==2
                  and r["operator"]==f"C{op}")
            eff["HEPfit_minus_author"]+=weights[3]*.0001
        x=close_numeric_comparison(obj)
        self.assertIn("REQUIRES_REVIEW",x["status"])
        self.assertFalse(x["HEPfit_matches_authors_C3_C6_exact_numerical"])

    def test_raw_dipole_preference_can_change_without_numerical_pass(self):
        obj=fixture()
        raw=next(r for r in obj["comparison_rows"] if
                  r["mass_GeV"]==2000 and r["author_order"]==3
                  and r["operator"]=="C7")
        raw["SuperIso_minus_author"]+=.1
        eff=next(r for r in obj["comparison_rows"] if
                  r["mass_GeV"]==2000 and r["author_order"]==2
                  and r["operator"]=="C7")
        eff["SuperIso_minus_author"]+=.1
        x=close_numeric_comparison(obj)
        self.assertIn("REQUIRES_REVIEW",x["status"])
        self.assertFalse(x["SuperIso_raw_C7_C8_closer_to_authors_all_8"])

if __name__=="__main__":
    unittest.main()
