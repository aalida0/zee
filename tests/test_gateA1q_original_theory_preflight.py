"""Gate A1Q author-source acquisition and non-overclaim regression tests."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1q_original_theory_preflight import (
    inspect_author_mathematica,audit,Y,Z,
)

def synthetic_candidate():
    # Synthetic fixture: deliberately NOT the official file.
    return (
        "(* Synthetic Mathematica matching fixture, NOT an author source *)\n"
        "cH[2,3] = a;\n"
        "cH[2,4] = b;\n"
        "cHeff[2,7] = c;\n"
        "cHeff[2,8] = d;\n"
        "c7t3L2HDM = e;\n"
        "c8t3L2HDM = f;\n"
        "cH3uuL[7] = g;\n"
        "cH3duL[8] = h;\n"
        + "(* fixture filler *)\n"*90
    )

class TestGateA1QSourcePreflight(unittest.TestCase):
    def test_missing_original_source_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=inspect_author_mathematica(pathlib.Path(tmp)/"c2HDM.m")
            self.assertEqual(
                result["status"],"BLOCKED_ORIGINAL_C2HDM_M_NOT_ACQUIRED")

    def test_html_download_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=pathlib.Path(tmp)/"c2HDM.m"
            f.write_text("<html><body>Not found</body></html>"+" "*2000)
            self.assertEqual(inspect_author_mathematica(f)["status"],
                             "BLOCKED_RETRIEVED_HTML_OR_ERROR_PAGE")

    def test_unknown_mathematica_symbols_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=pathlib.Path(tmp)/"c2HDM.m"
            f.write_text("(* arbitrary source without published symbols *)"+
                         "x=2;\n"*500)
            self.assertEqual(inspect_author_mathematica(f)["status"],
                             "BLOCKED_SOURCE_SYMBOL_CONTRACT_UNCONFIRMED")

    def test_candidate_fingerprint_never_means_theory_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=pathlib.Path(tmp)/"c2HDM.m"
            f.write_text(synthetic_candidate())
            result=inspect_author_mathematica(f)
            self.assertEqual(result["status"],
                "ORIGINAL_MATHEMATICA_CANDIDATE_FINGERPRINTED_NOT_EVALUATED")
            self.assertFalse(result["source_authenticity_proven_by_local_sha256"])
            self.assertFalse(result["analytic_C3_C4_log_comparison_pass"])
            self.assertFalse(result["dipole_normalization_evaluation_pass"])

    def test_a1q_does_not_claim_validated_nnlo_even_with_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=pathlib.Path(tmp)/"c2HDM.m"
            f.write_text(synthetic_candidate())
            result=audit(f,{"status":"fixture"})
            self.assertFalse(result["NNLO_matching_theoretically_validated"])
            self.assertFalse(result["full_TypeII_branching_ratio_validated"])
            self.assertIsNone(result["Zee_benchmark_excluded"])
            self.assertEqual(result["status"],
                "GATE_A1Q_BLOCKED_PENDING_ORIGINAL_THEORY_EVALUATION")

    def test_original_readme_effective_basis(self):
        self.assertEqual(Z["C5"],20.)
        self.assertEqual(Z["C3"],1.)
        self.assertAlmostEqual(Z["C4"],-1/6)
        self.assertAlmostEqual(Z["C6"],-10/3)
        self.assertEqual(Y["C5"],-20/3)
        self.assertEqual(Y["C6"],-80/9)

if __name__=="__main__":
    unittest.main()
