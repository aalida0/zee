"""Gate A1N: synthetic BR-candidate parser/validation, not vendor physics."""
from pathlib import Path
import json
import math
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1n_check_br_candidate import NAMES, parse_output, official_sm,verify


class TestCandidateValidation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.ref=self.root/"sm.txt"
        self.ref.write_text(
            "SuperIso v5.0 - 2025\nStandard Model predictions\n"
            "BR(b->s gamma)\t3.382e-04\n")
        self.native=self.root/"native.txt"
        self.patched=self.root/"patched.txt"
        self.fake(self.native,False)
        self.fake(self.patched,True)

    def fake(self,path,isolated):
        lines=["STATUS GATE_A1N_BR_CANDIDATE_NOT_VALIDATED_FOR_EXCLUSION",
               "INPUTS mH1=300 mH2=700 gamma=1.089"]
        sm=0.0003382
        for scale in range(5):
            diffs={
                "SM":0.,
                "TYPEII_300":.00012,"TYPEII_700":.00004,
                "TYPEII_1000":.00002,"TYPEII_2000":.000005,
                "ZEE_300_700":.00005,
                "ENDPOINT_H1":.00012,"ENDPOINT_H2":.00004
            }
            for name in sorted(NAMES):
                br=sm+diffs[name]*(1.03 if isolated else 1.)*(1+.01*scale)
                lines.append(f"RESULT {name} {br:.17g} muW=160.7384 "
                             f"mub=2.4 cpmax=0.00333156 scale={scale}")
                lines.append(f"CPDETAIL {name} C7p_re=0.00333156 "
                             f"C7p_im=0 C8p_re=0.001 C8p_im=0 "
                             f"scale={scale}")
        lines.append("STATUS_END GATE_A1N_BR_CANDIDATE_NO_EXCLUSION")
        path.write_text("\n".join(lines)+"\n")

    def test_valid_synthetic_controls(self):
        a=parse_output(self.native)
        b=parse_output(self.patched)
        r=verify(a,b,official_sm(self.ref))
        self.assertIn("CONTROLS_PASS",r["status"])
        self.assertIsNone(r["Zee_benchmark_allowed"])
        self.assertTrue(r["per_library"]["isolated"]
                        ["typeII_2000_closer_to_sm_than_1000"])
        self.assertAlmostEqual(r["nominal_primed_diagnostics"]["vendor"]["SM"]
                               ["C7prime_re"],0.00333156)
        self.assertTrue(r["primed_coefficients_unchanged_by_nlo_patch"])

    def test_missing_primed_row_rejected(self):
        contents=self.native.read_text().splitlines()
        self.native.write_text("\n".join(
            line for line in contents
            if not (line.startswith("CPDETAIL SM ") and line.endswith("scale=0"))
        )+"\n")
        with self.assertRaises(ValueError):
            parse_output(self.native)

    def test_nonzero_primed_coefficients_allowed(self):
        result=parse_output(self.native)
        self.assertAlmostEqual(result[0,"SM"]["cpmax"],0.00333156)
        self.assertAlmostEqual(result[0,"SM"]["C7prime_re"],0.00333156)

    def test_primed_coefficients_changed_by_patch_rejected(self):
        contents=self.patched.read_text().splitlines()
        ix=next(i for i,line in enumerate(contents)
                if line.startswith("CPDETAIL SM ") and line.endswith("scale=0"))
        contents[ix]=contents[ix].replace("C7p_re=0.00333156",
                                          "C7p_re=0.0032")
        self.patched.write_text("\n".join(contents)+"\n")
        with self.assertRaises(ValueError):
            verify(parse_output(self.native),parse_output(self.patched),
                   official_sm(self.ref))

    def test_omitted_result_rejected(self):
        contents=self.native.read_text()
        self.native.write_text("\n".join(
            line for line in contents.splitlines()
            if not line.startswith("RESULT TYPEII_300 ") )+"\n")
        with self.assertRaises(ValueError):
            parse_output(self.native)

    def test_bad_sm_reference_rejected(self):
        self.ref.write_text("BR(b->s gamma) 2.000e-04\n")
        with self.assertRaises(ValueError):
            verify(parse_output(self.native),
                   parse_output(self.patched),official_sm(self.ref))

    def test_endpoint_failure_rejected(self):
        contents=self.patched.read_text().splitlines()
        idx=next(i for i,v in enumerate(contents)
                 if v.startswith("RESULT ENDPOINT_H1 ") and v.endswith("scale=0"))
        parts=contents[idx].split()
        parts[2]="0.4"
        contents[idx]=" ".join(parts)
        self.patched.write_text("\n".join(contents)+"\n")
        with self.assertRaises(ValueError):
            verify(parse_output(self.native),parse_output(self.patched),
                   official_sm(self.ref))

    def test_truncated_footer_rejected(self):
        self.native.write_text(self.native.read_text().replace(
            "STATUS_END GATE_A1N_BR_CANDIDATE_NO_EXCLUSION",""))
        with self.assertRaises(ValueError):
            parse_output(self.native)

    def test_native_patched_sm_change_rejected(self):
        contents=self.patched.read_text().splitlines()
        ix=next(i for i,x in enumerate(contents)
                if x.startswith("RESULT SM ") and x.endswith("scale=0"))
        words=contents[ix].split()
        words[2]="0.0003500"
        contents[ix]=" ".join(words)
        self.patched.write_text("\n".join(contents)+"\n")
        with self.assertRaises(ValueError):
            verify(parse_output(self.native),
                   parse_output(self.patched),official_sm(self.ref))

if __name__=="__main__":
    unittest.main()
