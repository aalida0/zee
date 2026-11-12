"""Forensic tests of the two-chirality scalar isovector p/n nuclear repair.

Uses a synthetic excerpt of the 2017 SARAH FlavorKit observable as fixture;
does NOT impersonate the unavailable hash-locked ZeeTypeII original source.
"""
import unittest
from pathlib import Path
import tempfile
from research.full_constraints.lfv_64_native_2026.patch_original_nuclear_source import patch_text,patch

BASE="""! synthetic transcription from known common SARAH FlavorKit nuclear observable
Subroutine Calculate_MuEconversion(K1L,K1R,K2L,K2R)
  g0LS=(gSp+gSn)/2
  g1LS=(gSp-gSn)/2
  g0LV=(gVp+gVn)/2
  g1LV=(gVp-gVn)/2
  Lcont=(Znuc+Nnuc)*(g0LV+g0LS)+(Znuc-Nnuc)*(g1LV-g1LS)
  Rcont=(Znuc+Nnuc)*(g0RV+g0RS)+(Znuc-Nnuc)*(g1RV-g1RS)
End Subroutine Calculate_MuEconversion
"""

class OriginalNuclearRepairTests(unittest.TestCase):
    def test_correction_is_exact_two_isovector_scalar_signs_and_no_vector_change(self):
        corrected=patch_text(BASE)
        self.assertNotEqual(corrected,BASE)
        self.assertIn("(g1LV+g1LS)",corrected)
        self.assertIn("(g1RV+g1RS)",corrected)
        self.assertIn("g0LV+g0LS",corrected)
        self.assertIn("g0RV+g0RS",corrected)
        self.assertEqual(corrected.count("Lcont="),1)
        self.assertEqual(corrected.count("Rcont="),1)
        self.assertEqual(corrected.replace("(g1LV+g1LS)","(g1LV-g1LS)").replace(
            "(g1RV+g1RS)","(g1RV-g1RS)"),BASE)

    def test_real_scalar_nuclear_pn_contraction(self):
        Z,N,sp,sn,vp,vn=13,14,5.1,4.3,2.,1.
        g0S,g1S=(sp+sn)/2,(sp-sn)/2
        g0V,g1V=(vp+vn)/2,(vp-vn)/2
        original=(Z+N)*(g0V+g0S)+(Z-N)*(g1V-g1S)
        corrected=(Z+N)*(g0V+g0S)+(Z-N)*(g1V+g1S)
        self.assertAlmostEqual(original,(Z*vp+N*vn)+(N*sp+Z*sn))
        self.assertAlmostEqual(corrected,(Z*vp+N*vn)+(Z*sp+N*sn))
        self.assertNotAlmostEqual(original,corrected)

    def test_incomplete_wrong_or_already_patched_fortran_fails_closed(self):
        for source in (
            BASE.replace("Rcont=","RcontWrong="),
            BASE.replace("g1LV-g1LS","g1LV+g1LS"),
            BASE.replace("End Subroutine Calculate_MuEconversion",""),
        ):
            with self.assertRaises(ValueError):
                patch_text(source)

    def test_no_original_fortran_modified_and_wrong_original_hash_denied(self):
        with tempfile.TemporaryDirectory() as d:
            original=Path(d)/"FlavorKit_Observables_ZeeTypeII.f90"
            output=Path(d)/"patched.f90"
            original.write_text(BASE)
            with self.assertRaises(ValueError):patch(original,output)
            self.assertFalse(output.exists())
            self.assertEqual(original.read_text(),BASE)

if __name__=="__main__":
    unittest.main()
