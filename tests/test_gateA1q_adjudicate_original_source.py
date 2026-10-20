"""Gate A1Q static source adjudication must not claim numerical physics pass."""
from __future__ import annotations
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1q_adjudicate_original_source import adjudicate_author_static

def sample():
    return """(* Original KIT syntax fixture only *)
cH[2,3] = (Au*AuC*Log[mu^2/mt^2] + r);
cH[2,4] = (Au*AuC*(3*Log[mu^2/mt^2]+2*r));
cHeff[2,7] = (cH[3,7] - 1/3*cH[2,3] - 4/9*cH[2,4] - 20/3*cH[2,5] - 80/9*cH[2,6]);
cHeff[2,8] = (cH[3,8] + cH[2,3] - 1/6*cH[2,4] + 20*cH[2,5] - 10/3*cH[2,6]);
"""
def contracts():
    return {
        "HEPfit_NNLO_C8_minus20_C5_in_source":True,
        "SuperIso_effective_basis_checks":{"SuperIso_RG_effective_C8":True},
        "source_matching_log_checks":{
            "HEPfit_C3_uses_lstmu":True,
            "HEPfit_C4_uses_lstmu":True,
            "HEPfit_lstmu_log_top":True,
            "SuperIso_C3_uses_H_mass_in_log":True,
            "SuperIso_C4_uses_H_mass_in_log":True,
        },
    }
class TestA1QAuthorSourceStatic(unittest.TestCase):
    def test_original_log_and_sign_identified(self):
        x=adjudicate_author_static(sample(),contracts())
        self.assertEqual(x["original_C3_matching_log_argument"],"Log[mu^2/mt^2]")
        self.assertEqual(x["original_C8_effective_C5_coefficient"],20)
        self.assertEqual(x["pinned_HEPfit_C8_effective_C5_coefficient"],-20)
        self.assertTrue(all(x["checks"].values()))
        self.assertTrue(x["source_level_C8_sign_inconsistency_confirmed"])
        self.assertFalse(x["sources_mathematica_evaluated"])
        self.assertFalse(x["full_NNLO_matching_validated"])
        self.assertFalse(x["physical_BtoXs_gamma_validated"])
        self.assertIsNone(x["Zee_benchmark_excluded"])

    def test_authors_C3_wrong_mass_log_blocks(self):
        src=sample().replace("Au*AuC*Log[mu^2/mt^2]",
                             "Au*AuC*Log[mu^2/mH^2]")
        with self.assertRaisesRegex(ValueError,"authors_C3"):
            adjudicate_author_static(src,contracts())

    def test_authors_C4_wrong_mass_log_blocks(self):
        src=sample().replace("3*Log[mu^2/mt^2]","3*Log[mu^2/mH^2]")
        with self.assertRaisesRegex(ValueError,"authors_C4"):
            adjudicate_author_static(src,contracts())

    def test_authors_C8_opposite_sign_blocks(self):
        src=sample().replace("+ 20*cH[2,5]","- 20*cH[2,5]")
        with self.assertRaisesRegex(ValueError,"authors_C8"):
            adjudicate_author_static(src,contracts())

    def test_duplicate_author_definition_blocks(self):
        src=sample()+"\ncH[2,3] = r^2;\n"
        with self.assertRaisesRegex(ValueError,"exactly one"):
            adjudicate_author_static(src,contracts())

    def test_missing_hepfit_log_source_check_blocks(self):
        checks=contracts()
        checks["source_matching_log_checks"]["HEPfit_lstmu_log_top"]=False
        with self.assertRaisesRegex(ValueError,"hepfit_C3"):
            adjudicate_author_static(sample(),checks)

    def test_author_comment_fake_sign_does_not_pass(self):
        src=sample().replace("+ 20*cH[2,5]","- 20*cH[2,5]") + (
            "\n(* cHeff[2,8] = cH[3,8] + cH[2,3] - 1/6*cH[2,4]"
            " + 20*cH[2,5] - 10/3*cH[2,6]; *)")
        with self.assertRaisesRegex(ValueError,"authors_C8"):
            adjudicate_author_static(src,contracts())

if __name__=="__main__":
    unittest.main()
