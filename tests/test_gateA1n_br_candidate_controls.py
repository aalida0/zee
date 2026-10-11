"""Gate A1N: synthetic BR-candidate parser/validation, not vendor physics."""
from pathlib import Path
import json
import math
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1n_check_br_candidate import NAMES, parse_output, official_sm,verify
from gateA1n_trace_mass_context import diagnostic, load_stages


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
                "ZEE_SAME_WC_ALT_MASS_700":.00005,
                "ZEE_REPEAT_MASS_300":.00005,
                "ZEE_REPEAT_MASS_700":.00005,
                "ENDPOINT_H1":.00012,"ENDPOINT_H2":.00004
            }
            for name in sorted(NAMES):
                if name in ("ZEE_300_700","ZEE_SAME_WC_ALT_MASS_700",
                            "ZEE_REPEAT_MASS_300","ZEE_REPEAT_MASS_700"):
                    if name in ("ZEE_300_700","ZEE_SAME_WC_ALT_MASS_700"):
                        value=sm+diffs[name]*(1.03 if isolated else 1.)*(1+.01*scale)
                        lines.append(
                            f"BRCLONE {name} br_mass300={value:.17g} "
                            f"br_mass700={value:.17g} "
                            f"br_original={value:.17g} scale={scale}")
                    lines.append(f"INPUTMUTATION {name} max_abs=0 scale={scale}")
                    for op in range(1,11):
                        # Same evolved WCs and primed coefficients across
                        # residual-mass choices; only BR may depend on it.
                        lines.append(
                            f"RGEDETAIL {name} i={op} C0re={op/10.} "
                            f"C0im=0 C1re={op/20.} C1im=0 "
                            f"C2re={op/30.} C2im=0 scale={scale}")
                        lines.append(
                            f"CPALL {name} i={op} re={op/1000.} "
                            f"im=0 scale={scale}")
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

    def test_zee_residual_mass_context_dependence_rejected(self):
        rows=self.patched.read_text().splitlines()
        ix=next(i for i,row in enumerate(rows)
                if row.startswith("RESULT ZEE_SAME_WC_ALT_MASS_700 ")
                and row.endswith("scale=0"))
        parts=rows[ix].split()
        parts[2]=str(float(parts[2])+1e-6)
        rows[ix]=" ".join(parts)
        self.patched.write_text("\n".join(rows)+"\n")
        with self.assertRaisesRegex(ValueError,"residual point.mass_H"):
            verify(parse_output(self.native),parse_output(self.patched),
                   official_sm(self.ref))

    def test_mass_stage_diagnostic_finds_bsgamma_level_dependence(self):
        rows=self.native.read_text().splitlines()
        ix=next(i for i,row in enumerate(rows)
                if row.startswith("RESULT ZEE_SAME_WC_ALT_MASS_700 ")
                and row.endswith("scale=0"))
        fields=rows[ix].split()
        fields[2]=str(float(fields[2])-7.3e-7)
        rows[ix]=" ".join(fields)
        repeat_ix=next(i for i,row in enumerate(rows)
                  if row.startswith("RESULT ZEE_REPEAT_MASS_700 ")
                  and row.endswith("scale=0"))
        repeat_fields=rows[repeat_ix].split()
        repeat_fields[2]=fields[2]
        rows[repeat_ix]=" ".join(repeat_fields)
        self.native.write_text("\n".join(rows)+"\n")
        stage=diagnostic(self.native,self.patched,self.root)
        self.assertEqual(stage["libraries"]["vendor"]["stage_diagnosis"],
                         "UPSTREAM_PARAMETER_CONTEXT_DIFFERS_DESPITE_IDENTICAL_WCS")
        self.assertEqual(stage["libraries"]["vendor"]["scales"][0]
                         ["maximum_post_RG_WC_difference"],0.)

    def test_frozen_wilsons_isolate_bsgamma_mass_effect(self):
        lines=self.native.read_text().splitlines()
        ix=next(i for i,line in enumerate(lines)
                if line.startswith("BRCLONE ZEE_300_700 ")
                and line.endswith("scale=0"))
        # Pretend the final routine alone depends on arbitrary mass_H,
        # while the RGE and primed coefficients remain strictly fixed.
        fields=lines[ix].split()
        fields[3]=f"br_mass700={float(fields[2].split('=')[1])-7.3e-7:.17g}"
        lines[ix]=" ".join(fields)
        self.native.write_text("\n".join(lines)+"\n")
        stage=diagnostic(self.native,self.patched,self.root)
        self.assertEqual(stage["libraries"]["vendor"]["stage_diagnosis"],
                         "FROZEN_WCS_BSGAMMA_DEPENDS_ON_RESIDUAL_HIGGS_MASS")
        self.assertGreater(stage["libraries"]["vendor"]["scales"][0]
                           ["max_bsgamma_only_frozen_WC_mass_switch_difference"],0)

    def test_bsgamma_clone_missing_rejected(self):
        lines=self.native.read_text().splitlines()
        self.native.write_text("\n".join(
            x for x in lines
            if not (x.startswith("BRCLONE ZEE_300_700 ")
                    and x.endswith("scale=0"))) + "\n")
        with self.assertRaisesRegex(ValueError,"bsgamma-only"):
            load_stages(self.native)

    def test_mass_stage_diagnostic_finds_rg_difference(self):
        content=self.native.read_text()
        content=content.replace(
            "RGEDETAIL ZEE_SAME_WC_ALT_MASS_700 i=7 C0re=0.7",
            "RGEDETAIL ZEE_SAME_WC_ALT_MASS_700 i=7 C0re=0.6",1)
        content=content.replace(
            "RGEDETAIL ZEE_REPEAT_MASS_700 i=7 C0re=0.7",
            "RGEDETAIL ZEE_REPEAT_MASS_700 i=7 C0re=0.6",1)
        self.native.write_text(content)
        stage=diagnostic(self.native,self.patched,self.root)
        self.assertEqual(stage["libraries"]["vendor"]["stage_diagnosis"],
                         "POST_RG_DIFFERENCE_BETWEEN_MASS_CONTEXTS_CAUSE_NOT_ESTABLISHED")

    def test_mass_stage_diagnostic_finds_primed_difference(self):
        content=self.native.read_text()
        content=content.replace(
            "CPALL ZEE_SAME_WC_ALT_MASS_700 i=7 re=0.007",
            "CPALL ZEE_SAME_WC_ALT_MASS_700 i=7 re=0.006",1)
        content=content.replace(
            "CPALL ZEE_REPEAT_MASS_700 i=7 re=0.007",
            "CPALL ZEE_REPEAT_MASS_700 i=7 re=0.006",1)
        self.native.write_text(content)
        stage=diagnostic(self.native,self.patched,self.root)
        self.assertEqual(stage["libraries"]["vendor"]["stage_diagnosis"],
                         "PRIMED_WC_DIFFERENCE_BETWEEN_MASS_CONTEXTS")

    def test_mass_stage_detects_repeat_non_determinism(self):
        lines=self.native.read_text().splitlines()
        ix=next(i for i,line in enumerate(lines)
                if line.startswith("RGEDETAIL ZEE_REPEAT_MASS_300 i=7 ")
                and line.endswith("scale=0"))
        lines[ix]=lines[ix].replace("C0re=0.7","C0re=0.6")
        self.native.write_text("\n".join(lines)+"\n")
        stage=diagnostic(self.native,self.patched,self.root)
        self.assertEqual(stage["libraries"]["vendor"]["stage_diagnosis"],
                         "SAME_MASS_REPEAT_IS_NONDETERMINISTIC_CHECK_STATE_OR_MEMORY")

    def test_strict_validation_rejects_repeat_call_drift(self):
        lines=self.patched.read_text().splitlines()
        ix=next(i for i,line in enumerate(lines)
                if line.startswith("RESULT ZEE_REPEAT_MASS_300 ")
                and line.endswith("scale=0"))
        parts=lines[ix].split()
        parts[2]=str(float(parts[2])+8e-7)
        lines[ix]=" ".join(parts)
        self.patched.write_text("\n".join(lines)+"\n")
        with self.assertRaisesRegex(ValueError,"call-order/statefulness"):
            verify(parse_output(self.native),parse_output(self.patched),
                   official_sm(self.ref))

    def test_mass_stage_missing_rows_rejected(self):
        contents=self.native.read_text()
        self.native.write_text("\n".join(
            line for line in contents.splitlines()
            if not (line.startswith("RGEDETAIL ZEE_SAME_WC_ALT_MASS_700 i=4 ")
                    and line.endswith("scale=0"))
        )+"\n")
        with self.assertRaises(ValueError):
            load_stages(self.native)

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
