"""Gate 7 source-only Type-II patch tests. No Mathematica or MG5 required."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate7_prepare_typeii_feynrules import (
    REPLACEMENTS, SOURCE_FILES, patch_quark_yukawa, create
)

D="QLbar[sp, ii, ff1, cc].dR [sp, ff3, cc] H1[ii]"
U="QLbar[sp, ii, ff1, cc].uR [sp, ff2, cc] H1bar[jj]"


class SourcePatchTest(unittest.TestCase):
    def test_typeii_higgs_basis_mapping(self):
        initial=f"yukq = -yd*{D} - yu*{U};\n"
        result=patch_quark_yukawa(initial)
        self.assertIn("H1[ii] - Tan[beta]*H2[ii]",result)
        self.assertIn("H1bar[jj] + Cot[beta]*H2bar[jj]",result)
        self.assertEqual(result.count("\n"),initial.count("\n"))

    def test_refuses_missing_upstream_quark_terms(self):
        with self.assertRaisesRegex(ValueError,"Expected exactly one"):
            patch_quark_yukawa("No quark terms")

    def test_refuses_patch_twice(self):
        original=D+"\n"+U
        with self.assertRaises(ValueError):
            patch_quark_yukawa(patch_quark_yukawa(original))

    def test_feyn_rules_source_only_and_no_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            original=root/"original"
            original.mkdir()
            for name in SOURCE_FILES:
                (original/name).write_text(
                    "yukq="+D+"\n"+U+"\n" if name=="Lagrangian.fr" else "SOURCE\n"
                )
            output=root/"derived"
            create(original,output)
            self.assertTrue((output/"ZEE.fr").is_file())
            self.assertEqual((original/"Lagrangian.fr").read_text(),
                             "yukq="+D+"\n"+U+"\n")
            self.assertIn("Tan[beta]",(output/"Lagrangian.fr").read_text())
            self.assertFalse((output/"ZEE_UFO").exists())
            with self.assertRaises(FileExistsError):
                create(original,output)


if __name__=="__main__":
    unittest.main()
