"""Tests for isolated, non-validated LHInput SPheno.m model candidate."""
import tempfile
import unittest
from pathlib import Path
from .candidate_spheno_boundary import generate,run

BASE=("OnlyLowEnergySPheno = True;\n"
      "BoundaryLowScaleInput = {\n"
      "  {Lambda1,Lambda1Input},\n"
      "  {Ye,YeSM} };\n"
      "ListDecayParticles = {hh};\n")

class BoundaryCandidateTests(unittest.TestCase):
    def test_only_two_requested_entries_added(self):
        result=generate(BASE)
        self.assertIn("{fzee, LHInput[fzee]}",result)
        self.assertIn("{Ye2, LHInput[Ye2]}",result)
        self.assertEqual(result.count("BoundaryLowScaleInput"),1)
        self.assertEqual(result.count("{Ye,YeSM}"),1)
        self.assertIn("ListDecayParticles = {hh};",result)
    def test_reject_existing_matrix_boundary_or_wrong_model(self):
        for text in (BASE.replace("{Lambda1,Lambda1Input}","{Ye2, LHInput[Ye2]}"),
                     "BoundaryLowScaleInput = {{Ye,YeSM}};"):
            with self.assertRaises(ValueError):generate(text)
    def test_never_overwrite_original_and_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            original=root/"original.m";original.write_text(BASE)
            candidate=root/"candidate.m"
            receipt=run(original,candidate)
            self.assertEqual(original.read_text(),BASE)
            self.assertEqual(receipt["physics_LFV"],None)
            self.assertEqual(receipt["do_not_replace_original"],True)
            self.assertTrue(candidate.with_suffix(".m.audit.json").is_file())
            with self.assertRaises(FileExistsError):run(original,candidate)

if __name__=="__main__":unittest.main()
