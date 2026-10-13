"""Gate A1Q: source intake must not invent independent NNLO validation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1q_author_reference_intake import (
    SYMBOLS,Z,Y,original_reference_presence,make_report
)

class TestGateA1QReferenceIntake(unittest.TestCase):
    def test_original_missing_blocks(self):
        result=original_reference_presence(None)
        self.assertEqual(result["status"],"ORIGINAL_C2HDM_M_NOT_SUPPLIED")
        self.assertFalse(result["originality_verified"])
        report=make_report({},result,None)
        self.assertEqual(report["status"],
            "GATE_A1Q_BLOCKED_ORIGINAL_AUTHOR_SOURCE_NOT_SUPPLIED")
        self.assertFalse(report["NNLO_matching_validated"])
        self.assertIsNone(report["Zee_benchmark_allowed"])

    def test_candidate_checksum_only_does_not_authenticate_origin(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"c2HDM.m"
            p.write_text("(* synthetic fixture; NOT author source *)\n"+
                "\n".join(f"{sym}[0] := 0;" for sym in SYMBOLS)+
                "\n"+"x=1;"*160)
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            intake=original_reference_presence(p,sha)
            self.assertTrue(intake["expected_hash_matches"])
            self.assertFalse(intake["originality_verified"])
            self.assertFalse(intake["Mathematica_expressions_evaluated"])
            report=make_report({},intake,"fixture://not-authenticated")
            self.assertEqual(report["status"],
                "GATE_A1Q_CANDIDATE_SOURCE_INTAKE_NOT_AUTHENTICATED")
            self.assertFalse(report["NNLO_matching_validated"])
            self.assertFalse(report["physical_BtoXs_gamma_validated"])

    def test_mismatched_hash_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"c2HDM.m"
            p.write_text(" ".join(SYMBOLS)+"\n"+"y=1;"*160)
            with self.assertRaisesRegex(ValueError,"expected SHA256 mismatch"):
                original_reference_presence(p,"0"*64)

    def test_synthetic_incomplete_source_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"c2HDM.m"
            p.write_text("cHeff\n"+"x=1;"*160)
            with self.assertRaisesRegex(ValueError,"symbols incomplete"):
                original_reference_presence(p)

    def test_wrong_source_filename_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"not_the_author_source.m"
            p.write_text(" ".join(SYMBOLS)+"\n"+"x=1;"*160)
            with self.assertRaisesRegex(ValueError,"named c2HDM.m"):
                original_reference_presence(p)

    def test_published_2012_standard_basis_vectors_are_explicit(self):
        self.assertEqual(Y[2:],[ -1/3,-4/9,-20/3,-80/9])
        self.assertEqual(Z[2:],[1,-1/6,20,-10/3])
        report=make_report({},original_reference_presence(None),None)
        self.assertIn("4*pi/alpha_s",
            report["published_source_author_README_basis"][
                "C7_C8_operator_normalization"])

if __name__=="__main__":
    unittest.main()
