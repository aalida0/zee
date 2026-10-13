"""Gate A1Q: test that authentic original-source static inspection fails closed."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import gateA1q_inspect_original_mathematica as mod

class TestA1QOriginalMathematicaStaticInspection(unittest.TestCase):
    def test_nested_comments_not_mistaken_for_definitions(self):
        src=("(* cH[2,3]=10; (* cHeff[2,8]=99; *) end *)\n"
             "cH[2,3] = (Log[mu^2/mt^2] + r);\n"
             's="cH[2,3] = fakesource";\n')
        matches=mod.extract_assignments(src,mod.SELECTORS["C3_NNLO"])
        self.assertEqual(len(matches),1)
        self.assertEqual(matches[0]["line"],2)
        self.assertEqual(matches[0]["symbol_counts"]["Log"],1)
        self.assertNotIn("fakesource",matches[0]["source_excerpt"])
        self.assertTrue(matches[0]["terminated_by_semicolon"])
        self.assertEqual(mod.extract_assignments(
            src,mod.SELECTORS["C8_NNLO_effective"]),[])

    def test_assignment_semicolon_nested_in_list_is_not_terminator(self):
        src="cHeff[2,8] := Module[{x=1; y=2;}, x+y+Log[r]];\n"
        found=mod.extract_assignments(
            src,mod.SELECTORS["C8_NNLO_effective"])
        self.assertEqual(len(found),1)
        self.assertIn("Log[r]",found[0]["source_excerpt"])
        self.assertTrue(found[0]["terminated_by_semicolon"])

    def test_unclosed_mathematica_comment_blocks(self):
        with self.assertRaisesRegex(ValueError,"Unterminated"):
            mod.strip_mathematica_comments("cH[2,3]=1; (* open")

    def test_exact_official_checksum_and_url_contract(self):
        raw=("cH[2,3] = 2; cH[2,4] = 3; cHeff[2,8] = 9;\n").encode()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            src=root/"c2HDM.m"
            src.write_bytes(raw)
            sha=hashlib.sha256(raw).hexdigest()
            info={
                "status":mod.EXPECTED_MANIFEST_STATUS,
                "resolved_source_url":mod.ORIGINAL_KIT_URL,
                "c2HDM_m_sha256":sha,
                "original_source_numerically_evaluated":False,
            }
            manifest=root/"kit_source_provenance.json"
            manifest.write_text(json.dumps(info))
            with patch.object(mod,"PINNED_KIT_SHA256",sha):
                content,digest,p=mod.attest_source(src,manifest)
                result=mod.audit(content,digest,p)
            self.assertEqual(len(result["symbol_literal_assignment_evidence"][
                "C3_NNLO"]),1)
            self.assertFalse(result["full_NNLO_matching_validated"])
            self.assertFalse(result["C3_C4_log_prescription_adjudicated"])
            self.assertFalse(result["C8_operator_sign_adjudicated"])
            self.assertFalse(result["Mathematica_expressions_evaluated"])
            self.assertIsNone(result["Zee_benchmark_excluded"])

    def test_sha256_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            src=root/"c2HDM.m"
            src.write_text("mock input")
            manifest=root/"kit_source_provenance.json"
            manifest.write_text("{}")
            with self.assertRaisesRegex(ValueError,"pinned SHA256"):
                mod.attest_source(src,manifest)

    def test_official_url_identity_is_mandatory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            src=root/"c2HDM.m"
            src.write_text("mock")
            sha=hashlib.sha256(src.read_bytes()).hexdigest()
            manifest=root/"kit_source_provenance.json"
            manifest.write_text(json.dumps({
                "status":mod.EXPECTED_MANIFEST_STATUS,
                "resolved_source_url":"https://evil.example.org/c2HDM.m",
                "c2HDM_m_sha256":sha,
                "original_source_numerically_evaluated":False,
            }))
            with patch.object(mod,"PINNED_KIT_SHA256",sha):
                with self.assertRaisesRegex(ValueError,"exact official KIT"):
                    mod.attest_source(src,manifest)

if __name__=="__main__":
    unittest.main()
